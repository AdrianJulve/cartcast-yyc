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
    assert "jobstatusdesc in ('Licensed', 'Pending Renewal')" in q
    assert "upper(tradename) like '%SUPERSTORE%'" in q
