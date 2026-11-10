from cartcast.sources import build_store_query
from cartcast.stores import classify, load_stores


def test_classify(cfg):
    s = cfg.settings
    assert classify("Real Canadian Superstore", s) == "supermarket"
    assert classify("Corner Halal Grocery", s) == "specialty"
    assert classify("Sunday Flea Market", s) is None
    assert classify("Bob's Auto", s) is None


def test_classify_matches_whole_words_and_excludes_non_grocers(cfg):
    s = cfg.settings
    # Real names from the City of Calgary licence data that are not grocers.
    for name in [
        "Delight Music School",
        "Calgary Florists - Calgary Flowers Delivery",
        "Calgary Metal Market",
        "All The Smoke Premium Cannabis Market",
        "Bon A-Pet-Treat! Pet Store & Bakery",
        "Deling Innovations Ca",
        "Flower Market (The)",
    ]:
        assert classify(name, s) is None, name
    # Real grocers that must still be included.
    assert classify("Afghan Bakery And Butcher Store", s) == "specialty"
    assert classify("Bulk Barn Foods", s) == "specialty"
    assert classify("Al-Noor Halal Meat And Grocery Store", s) == "specialty"
    assert classify("Calgary Co-op Markets", s) == "supermarket"
    assert classify("T & T Supermarket", s) == "supermarket"


def test_load_stores_filters_and_dedupes(stores_json, cfg):
    df = load_stores(stores_json, cfg.settings)
    assert sorted(df["name"]) == ["Corner Halal Grocery", "Safeway #12"]
    row = df[df["name"] == "Safeway #12"].iloc[0]
    assert row["kind"] == "supermarket"
    assert (row["lat"], row["lon"]) == (51.04, -114.07)
    assert row["community"] == "Beltline"


def test_store_query_has_all_clauses(cfg):
    q = build_store_query(cfg.settings)
    assert "licencetypes like '%RETAIL DEALER - PREMISES%'" in q
    assert "'Renewal Licensed'" in q and "'Renewal Invoiced'" in q
    assert "'Close in Progress'" not in q
    assert "upper(tradename) like '%REAL CANADIAN%'" in q
    assert "licencetypes like '%WHOLESALER%'" in q


def test_food_retailer_kind_uses_licence_types(cfg):
    from cartcast.stores import food_retailer_kind

    s = cfg.settings
    retail = "FOOD SERVICE - PREMISES, RETAIL DEALER - PREMISES"
    cases = {
        # Real records from the City of Calgary licence data.
        ("SAFEWAY #280", retail): "supermarket",
        (
            "CALGARY CO-OP #04",
            "FOOD SERVICE - PREMISES (SEATING), MARKET, RETAIL DEALER - PREMISES, TOBACCO RETAILER",
        ): "supermarket",
        ("WAL-MART CANADA #3009", retail): "supermarket",
        ("WAL-MART SUPERCENTRE #1136", retail): "supermarket",
        ("ANDREWS NO FRILLS", retail): "supermarket",
        ("WALKER LAKE MEAT SHOP", "FOOD SERVICE - PREMISES (NO SEATING)"): "specialty",
        (
            "SAFEWAY LIQUOR SOUTHTRAIL",
            "FOOD SERVICE - PREMISES, LIQUOR STORE, RETAIL DEALER - PREMISES",
        ): None,
        (
            "CALGARY CO-OP GAS BAR #26",
            "FOOD SERVICE - PREMISES, FUEL SALES/STORAGE, RETAIL DEALER - PREMISES",
        ): None,
        ("CALGARY CO-OP CANNABIS SHAWNESSY", "CANNABIS STORE, RETAIL DEALER - PREMISES"): None,
        (
            "CALGARY CO-OP HOME HEALTH CARE - MACLEOD TR",
            "RETAIL DEALER - PREMISES, WHOLESALER",
        ): None,
        (
            "CALGARY CO-OP TOUCHLESS CAR WASH #09",
            "MOTOR VEHICLE REPAIR AND SERVICE (2-PROV N/R)",
        ): None,
        ("WAL-MART PORTRAIT STUDIO #3010", "PHOTOGRAPHER"): None,
        ("AFC ZENSHI AT SAFEWAY 8841", "FOOD SERVICE - PREMISES (NO SEATING)"): None,
        ("AFC ZENSHI AT SOBEYS 4057", retail): None,
        # Supermarkets with a fuel licence on the same record.
        (
            "REAL CANADIAN SUPERSTORE (THE)",
            "FOOD SERVICE - PREMISES, FUEL SALES/STORAGE, RETAIL DEALER - PREMISES",
        ): "supermarket",
        (
            "SILVERADO SOBEYS",
            "FOOD SERVICE - PREMISES, FUEL SALES/STORAGE, RETAIL DEALER - PREMISES",
        ): "supermarket",
        # Costco holds a wholesaler licence, not a retail one.
        (
            "COSTCO WHOLESALE",
            "TOBACCO RETAILER, FUEL SALES/STORAGE, MOTOR VEHICLE REPAIR AND SERVICE (1), "
            "WHOLESALER, FOOD SERVICE - PREMISES (SEATING)",
        ): "supermarket",
        ("COSTCO LIQUOR", "LIQUOR STORE"): None,
        ("SOBEYS WESTERN CELLARS MILLRISE", "FOOD SERVICE - PREMISES, LIQUOR STORE"): None,
        # Independent supermarkets with only a food service licence.
        ("TOPS SUPERMARKET", "FOOD SERVICE - PREMISES, TOBACCO RETAILER"): "supermarket",
        ("SOBEYS WEST DISTRICT 4066", "FOOD SERVICE - PREMISES"): "supermarket",
        # Chain gas bars stay out by name.
        (
            "SUPERSTORE GAS BAR",
            "FOOD SERVICE - PREMISES, FUEL SALES/STORAGE, RETAIL DEALER - PREMISES",
        ): None,
        # "Superstore" alone is not a grocer.
        ("STAPLES THE OFFICE SUPERSTORE #110", retail): None,
        ("FLOORING SUPERSTORES", "RETAIL DEALER - PREMISES, WHOLESALER"): None,
        ("CARPET SUPERMARKET", "RETAIL DEALER - PREMISES"): None,
    }
    for (name, types), want in cases.items():
        assert food_retailer_kind({"tradename": name, "licencetypes": types}, s) == want, name
