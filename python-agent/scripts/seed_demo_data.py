#!/usr/bin/env python3
"""Seed the database with realistic demo data for electronic component sourcing."""

from datetime import date, datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from bom_agent_service.db import init_db
from bom_agent_service.stores import OrgKnowledgeStore
from bom_agent_service.models import (
    PartKnowledge,
    SupplierKnowledge,
    CategoryKnowledge,
    SupplierType,
    TrustLevel,
)


def seed_suppliers(store: OrgKnowledgeStore) -> None:
    """Seed supplier data."""
    suppliers = [
        # Tier 1 - High trust authorized distributors
        SupplierKnowledge(
            supplier_id="digikey",
            name="Digi-Key Electronics",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.96,
            quality_rate=0.995,
            lead_time_accuracy=0.92,
            account_rep="Sarah Chen",
            account_rep_email="schen@digikey.com",
            payment_terms="Net 30",
            credit_limit=50000.0,
            notes=[
                "[system 2024-06-15] Excellent fill rates on passive components",
                "[jsmith 2024-09-20] Fast response on expedite requests",
            ],
            last_order_date=date(2026, 1, 5),
            total_spend_ytd=125000.0,
            order_count_ytd=47,
        ),
        SupplierKnowledge(
            supplier_id="mouser",
            name="Mouser Electronics",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.94,
            quality_rate=0.992,
            lead_time_accuracy=0.90,
            account_rep="Mike Rodriguez",
            account_rep_email="mrodriguez@mouser.com",
            payment_terms="Net 30",
            credit_limit=40000.0,
            notes=[
                "[system 2024-07-10] Strong inventory on semiconductors",
                "[procurement 2024-11-15] Good pricing on TI parts",
            ],
            last_order_date=date(2026, 1, 8),
            total_spend_ytd=98000.0,
            order_count_ytd=38,
        ),
        SupplierKnowledge(
            supplier_id="newark",
            name="Newark Electronics",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.91,
            quality_rate=0.988,
            lead_time_accuracy=0.88,
            account_rep="David Kim",
            account_rep_email="dkim@newark.com",
            payment_terms="Net 30",
            credit_limit=30000.0,
            notes=["[system 2024-05-20] Good for connectors and electromechanicals"],
            last_order_date=date(2024, 12, 18),
            total_spend_ytd=45000.0,
            order_count_ytd=22,
        ),
        SupplierKnowledge(
            supplier_id="arrow",
            name="Arrow Electronics",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.93,
            quality_rate=0.990,
            lead_time_accuracy=0.89,
            account_rep="Jennifer Wu",
            account_rep_email="jwu@arrow.com",
            payment_terms="Net 45",
            credit_limit=75000.0,
            notes=[
                "[system 2024-08-01] Strong on STMicro and NXP lines",
                "[engineering 2024-10-05] Helped with reference designs",
            ],
            last_order_date=date(2026, 1, 3),
            total_spend_ytd=180000.0,
            order_count_ytd=29,
        ),
        SupplierKnowledge(
            supplier_id="avnet",
            name="Avnet",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.92,
            quality_rate=0.991,
            lead_time_accuracy=0.87,
            account_rep="Tom Anderson",
            account_rep_email="tanderson@avnet.com",
            payment_terms="Net 45",
            credit_limit=60000.0,
            notes=["[system 2024-06-01] Good for high-volume pricing"],
            last_order_date=date(2024, 12, 20),
            total_spend_ytd=72000.0,
            order_count_ytd=15,
        ),
        # Tier 2 - Medium trust distributors
        SupplierKnowledge(
            supplier_id="lcsc",
            name="LCSC Electronics",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.MEDIUM,
            on_time_rate=0.85,
            quality_rate=0.96,
            lead_time_accuracy=0.75,
            payment_terms="Prepaid",
            notes=[
                "[procurement 2024-09-01] Good for Chinese components, longer lead times",
                "[engineering 2024-11-10] Verify datasheets match - some translation issues",
            ],
            last_order_date=date(2024, 11, 25),
            total_spend_ytd=15000.0,
            order_count_ytd=8,
        ),
        SupplierKnowledge(
            supplier_id="tme",
            name="TME Electronic Components",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.MEDIUM,
            on_time_rate=0.88,
            quality_rate=0.97,
            lead_time_accuracy=0.82,
            payment_terms="Net 30",
            notes=["[system 2024-07-15] European distributor, good for EU compliance parts"],
            last_order_date=date(2024, 10, 15),
            total_spend_ytd=8500.0,
            order_count_ytd=5,
        ),
        # Broker - Low trust, use with caution
        SupplierKnowledge(
            supplier_id="smith_and_assoc",
            name="Smith & Associates",
            supplier_type=SupplierType.BROKER,
            trust_level=TrustLevel.LOW,
            on_time_rate=0.80,
            quality_rate=0.92,
            lead_time_accuracy=0.70,
            payment_terms="Prepaid",
            notes=[
                "[procurement 2024-03-15] Use only for obsolete parts with full testing",
                "[quality 2024-08-20] Requires incoming inspection on all orders",
            ],
            last_order_date=date(2024, 8, 15),
            total_spend_ytd=12000.0,
            order_count_ytd=3,
        ),
        # Untrusted supplier (effectively blocked)
        SupplierKnowledge(
            supplier_id="alibaba_generic",
            name="Various Alibaba Sellers",
            supplier_type=SupplierType.BROKER,
            trust_level=TrustLevel.LOW,
            on_time_rate=0.60,
            quality_rate=0.70,
            notes=[
                "[quality 2024-01-10] DO NOT USE: Multiple counterfeit incidents",
                "[engineering 2024-02-05] Found remarked chips from this source",
                "[procurement 2024-02-10] Removed from approved vendor list",
            ],
        ),
    ]

    for supplier in suppliers:
        existing = store.get_supplier(supplier.supplier_id)
        if not existing:
            store._save_supplier(supplier)
            print(f"  Created supplier: {supplier.name}")
        else:
            print(f"  Supplier exists: {supplier.name}")


def seed_parts(store: OrgKnowledgeStore) -> None:
    """Seed part knowledge data."""
    parts = [
        # Resistors
        PartKnowledge(
            mpn="RC0805FR-0710KL",
            notes=[
                "[system 2024-06-01] Standard 10K resistor, excellent availability",
                "[engineering 2024-09-15] Verified AEC-Q200 qualified",
            ],
            approved_alternates=["ERJ-6ENF1002V", "CRCW080510K0FKEA"],
            preferred=True,
            last_used_date=date(2026, 1, 5),
            projects_used_in=["PRJ-2024-015", "PRJ-2024-022", "PRJ-2026-001"],
            times_used=15,
            failure_count=0,
        ),
        PartKnowledge(
            mpn="ERJ-6ENF1002V",
            notes=["[engineering 2024-07-20] Panasonic equivalent to Yageo RC0805"],
            approved_alternates=["RC0805FR-0710KL"],
            preferred=False,
            times_used=3,
            failure_count=0,
        ),
        # Capacitors
        PartKnowledge(
            mpn="ECA-1EM101",
            notes=[
                "[system 2024-05-10] Standard 100uF electrolytic",
                "[engineering 2024-08-01] Good for general purpose, not for high-temp",
            ],
            approved_alternates=["UVR1E101MDD", "EEU-FC1E101"],
            last_used_date=date(2024, 12, 10),
            projects_used_in=["PRJ-2024-018", "PRJ-2026-001"],
            times_used=8,
            failure_count=0,
        ),
        PartKnowledge(
            mpn="CL21B104KBCNNNC",
            notes=[
                "[system 2024-04-15] Samsung 0.1uF MLCC - high reliability",
                "[engineering 2024-10-20] Excellent for decoupling",
            ],
            approved_alternates=["GRM21BR71H104KA01L", "C0805C104K5RACTU"],
            preferred=True,
            last_used_date=date(2026, 1, 8),
            projects_used_in=["PRJ-2024-010", "PRJ-2024-015", "PRJ-2024-022", "PRJ-2026-001"],
            times_used=22,
            failure_count=0,
        ),
        # MCU
        PartKnowledge(
            mpn="ATMEGA328P-PU",
            notes=[
                "[system 2024-03-01] Legacy Arduino MCU - consider migration to newer parts",
                "[engineering 2024-06-15] Limited flash (32KB) - OK for simple projects",
                "[sourcing 2024-09-01] NRND status - verify availability before design-in",
            ],
            approved_alternates=["ATMEGA328PB-AU", "ATMEGA4809-AFR"],
            last_used_date=date(2024, 11, 20),
            projects_used_in=["PRJ-2024-005", "PRJ-2026-001"],
            times_used=5,
            failure_count=0,
            quality_notes=["EOL risk - plan migration path"],
        ),
        PartKnowledge(
            mpn="STM32F401RET6",
            notes=[
                "[system 2024-02-15] Recommended replacement for ATMEGA328P",
                "[engineering 2024-05-10] 512KB flash, 84MHz, excellent for IoT",
            ],
            approved_alternates=["STM32F401RCT6", "STM32F411RET6"],
            preferred=True,
            last_used_date=date(2026, 1, 3),
            projects_used_in=["PRJ-2024-012", "PRJ-2024-020", "PRJ-2024-025"],
            times_used=12,
            failure_count=0,
        ),
        # Voltage Regulators
        PartKnowledge(
            mpn="LM7805CT",
            notes=[
                "[system 2024-04-01] Classic linear regulator - low efficiency",
                "[engineering 2024-07-10] Consider switching regulator for battery apps",
            ],
            approved_alternates=["L7805CV", "MC7805ACTG"],
            last_used_date=date(2024, 10, 15),
            projects_used_in=["PRJ-2024-008", "PRJ-2026-001"],
            times_used=10,
            failure_count=1,
            quality_notes=["One failure in PRJ-2024-008 due to thermal issue - ensure proper heatsinking"],
        ),
        PartKnowledge(
            mpn="AP2112K-3.3TRG1",
            notes=[
                "[system 2024-05-20] Low dropout 3.3V LDO - excellent for battery",
                "[engineering 2024-08-15] 600mA output, very low quiescent current",
            ],
            approved_alternates=["MIC5219-3.3YM5-TR", "TLV70233DBVR"],
            preferred=True,
            last_used_date=date(2026, 1, 5),
            projects_used_in=["PRJ-2024-015", "PRJ-2024-022"],
            times_used=8,
            failure_count=0,
        ),
        # USB Connector
        PartKnowledge(
            mpn="12401610E4#2A",
            notes=[
                "[system 2024-06-10] Amphenol USB-C - excellent quality",
                "[engineering 2024-09-05] Mid-mount, good for thin designs",
            ],
            approved_alternates=["USB4110-GF-A", "632712000011"],
            last_used_date=date(2024, 12, 20),
            projects_used_in=["PRJ-2024-018", "PRJ-2026-001"],
            times_used=6,
            failure_count=0,
        ),
        # Crystal
        PartKnowledge(
            mpn="ABL-16.000MHZ-B2",
            notes=[
                "[system 2024-03-15] Standard 16MHz crystal",
                "[engineering 2024-06-01] 20ppm tolerance - OK for most applications",
            ],
            approved_alternates=["ECS-160-20-3X-TR", "FOXSDLF/160-20"],
            last_used_date=date(2024, 11, 10),
            projects_used_in=["PRJ-2024-005", "PRJ-2026-001"],
            times_used=7,
            failure_count=0,
        ),
        # Transistors and Diodes
        PartKnowledge(
            mpn="2N2222A",
            notes=["[system 2024-02-01] Classic NPN transistor - widely available"],
            approved_alternates=["PN2222A", "MMBT2222A"],
            last_used_date=date(2024, 9, 15),
            projects_used_in=["PRJ-2024-003", "PRJ-2026-001"],
            times_used=12,
            failure_count=0,
        ),
        PartKnowledge(
            mpn="1N4007-E3/54",
            notes=["[system 2024-01-15] Standard rectifier diode - 1A 1000V"],
            approved_alternates=["1N4007", "US1M"],
            last_used_date=date(2024, 10, 20),
            projects_used_in=["PRJ-2024-008", "PRJ-2026-001"],
            times_used=9,
            failure_count=0,
        ),
        # LEDs
        PartKnowledge(
            mpn="WP7113ID",
            notes=[
                "[system 2024-04-20] Standard red 3mm LED",
                "[engineering 2024-07-15] Good brightness, verify forward voltage",
            ],
            approved_alternates=["SSL-LX3044ID", "HLMP-1301"],
            last_used_date=date(2024, 11, 25),
            projects_used_in=["PRJ-2024-010", "PRJ-2026-001"],
            times_used=14,
            failure_count=0,
        ),
        # Banned part example
        PartKnowledge(
            mpn="FAKE-CHIP-001",
            notes=[
                "[quality 2024-02-10] BANNED: Known counterfeit part number",
                "[engineering 2024-02-10] Found in supply chain with remarked dies",
            ],
            banned=True,
            ban_reason="Confirmed counterfeit - remarked dies with incorrect specifications",
            times_used=0,
            failure_count=2,
            quality_notes=["Field failures in PRJ-2023-042", "Do not use under any circumstances"],
        ),
    ]

    for part in parts:
        existing = store.get_part(part.mpn)
        if not existing:
            store._save_part(part)
            print(f"  Created part: {part.mpn}")
        else:
            print(f"  Part exists: {part.mpn}")


def seed_categories(store: OrgKnowledgeStore) -> None:
    """Seed category knowledge."""
    categories = [
        CategoryKnowledge(
            category="0805 Chip Resistors",
            preferred_manufacturers=["Yageo", "Vishay", "Panasonic", "KOA"],
            avoid_manufacturers=[],
            typical_lead_time_days=5,
            notes="Standard footprint, excellent availability. Prefer 1% tolerance for precision applications.",
        ),
        CategoryKnowledge(
            category="MLCC Capacitors",
            preferred_manufacturers=["Samsung", "Murata", "TDK", "Yageo"],
            avoid_manufacturers=["Unknown Chinese brands"],
            typical_lead_time_days=7,
            notes="Watch for DC bias derating on X5R/X7R. Use C0G for precision circuits.",
        ),
        CategoryKnowledge(
            category="Electrolytic Capacitors",
            preferred_manufacturers=["Panasonic", "Nichicon", "Rubycon"],
            avoid_manufacturers=["Lelon", "CapXon"],
            typical_lead_time_days=10,
            notes="Check ESR and ripple current ratings. Panasonic FM series excellent for switching supplies.",
        ),
        CategoryKnowledge(
            category="ARM Cortex-M MCUs",
            preferred_manufacturers=["STMicroelectronics", "NXP", "Microchip"],
            avoid_manufacturers=[],
            typical_lead_time_days=14,
            notes="STM32 series preferred for new designs. Check for AEC-Q100 for automotive.",
        ),
        CategoryKnowledge(
            category="Linear Voltage Regulators",
            preferred_manufacturers=["Texas Instruments", "Analog Devices", "Microchip"],
            avoid_manufacturers=[],
            typical_lead_time_days=10,
            notes="Consider thermal dissipation. Use LDOs for low-dropout requirements.",
        ),
        CategoryKnowledge(
            category="USB Connectors",
            preferred_manufacturers=["Amphenol", "Molex", "TE Connectivity", "Wurth"],
            avoid_manufacturers=["Generic unbranded"],
            typical_lead_time_days=12,
            notes="USB-C recommended for new designs. Check for USB-IF certification.",
        ),
        CategoryKnowledge(
            category="Crystals and Oscillators",
            preferred_manufacturers=["Abracon", "ECS", "NDK", "Epson"],
            avoid_manufacturers=[],
            typical_lead_time_days=8,
            notes="Match load capacitance to MCU requirements. Consider MEMS for vibration-sensitive apps.",
        ),
    ]

    for cat in categories:
        existing = store.get_category(cat.category)
        if not existing:
            store._save_category(cat)
            print(f"  Created category: {cat.category}")
        else:
            print(f"  Category exists: {cat.category}")


def main():
    print("Initializing database...")
    init_db()

    store = OrgKnowledgeStore()

    print("\nSeeding suppliers...")
    seed_suppliers(store)

    print("\nSeeding parts...")
    seed_parts(store)

    print("\nSeeding categories...")
    seed_categories(store)

    print("\n" + "=" * 50)
    print("Demo data seeding complete!")
    print("=" * 50)

    # Print summary
    suppliers = store.list_suppliers(limit=100)
    parts = store.list_parts(limit=100)
    print(f"\nDatabase now contains:")
    print(f"  - {len(suppliers)} suppliers")
    print(f"  - {len(parts)} parts")
    print(f"  - Categories seeded")

    # Show some examples
    print("\nHigh-trust suppliers:")
    for s in suppliers:
        if s.trust_level == TrustLevel.HIGH:
            print(f"  - {s.name} (YTD spend: ${s.total_spend_ytd:,.2f})")

    print("\nPreferred parts:")
    for p in parts:
        if p.preferred:
            print(f"  - {p.mpn} (used {p.times_used}x)")

    print("\nBanned parts:")
    for p in parts:
        if p.banned:
            print(f"  - {p.mpn}: {p.ban_reason}")


if __name__ == "__main__":
    main()
