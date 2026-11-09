import pytest

from cartcast.cpi import latest_yoy, load_cpi

HEADER = (
    "REF_DATE,GEO,DGUID,Products and product groups,UOM,UOM_ID,SCALAR_FACTOR,SCALAR_ID,"
    "VECTOR,COORDINATE,VALUE,STATUS,SYMBOL,TERMINATED,DECIMALS\n"
)


def _write(tmp_path, rows):
    body = "".join(f"{d},{g},,{p},2002=100,17,units,0,v1,1.1,{v},,,,1\n" for d, g, p, v in rows)
    path = tmp_path / "cpi.csv"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_load_cpi_filters_and_computes_yoy(tmp_path):
    rows = []
    for m in range(1, 13):
        rows.append((f"2025-{m:02d}", "Alberta", "Food purchased from stores", 100 + m))
    rows.append(("2026-01", "Alberta", "Food purchased from stores", 105.04))  # +4% vs 101
    rows.append(("2026-01", "Alberta", "Shelter", 999))
    rows.append(("2026-01", "Ontario", "Food purchased from stores", 999))
    path = _write(tmp_path, rows)

    cpi = load_cpi(path, ["Alberta"], ["Food purchased from stores"], chunksize=5)
    assert set(cpi["product"]) == {"Food purchased from stores"}
    assert set(cpi["geo"]) == {"Alberta"}
    month, yoy = latest_yoy(cpi, "Alberta", "Food purchased from stores")
    assert month.strftime("%Y-%m") == "2026-01"
    assert yoy == pytest.approx(4.0)


def test_load_cpi_no_match_raises(tmp_path):
    path = _write(tmp_path, [("2026-01", "Alberta", "Shelter", 150)])
    with pytest.raises(ValueError):
        load_cpi(path, ["Alberta"], ["All-items"])
