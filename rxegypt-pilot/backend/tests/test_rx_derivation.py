"""Guard the conservative Rx-derivation rules used when importing the verified
Egyptian dataset (which has no prescription/OTC field). The safe default is
prescription-only; only explicit non-prescription classes are OTC.
"""
import importlib.util
from pathlib import Path

# Load build_egyptian_drugs.py (lives under seed/, not a package).
_spec = importlib.util.spec_from_file_location(
    "build_egyptian_drugs",
    Path(__file__).resolve().parent.parent / "seed" / "build_egyptian_drugs.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
derive_rx = _mod.derive_rx


def test_unknown_class_defaults_to_prescription():
    assert derive_rx("") is True
    assert derive_rx(".") is True
    assert derive_rx("SOME UNCLASSIFIED THING") is True


def test_known_prescription_classes_are_rx():
    for cls in [
        "ANTIBIOTIC.QUINOLONE",
        "PSYCHIATRIC.ANTIPSYCHOTICS",
        "ANTINEOPLASTIC",
        "ANTIHYPERLIPIDEMIC.STATINS",
        "CARDIOVASCULAR",
        "ANTIDIABETIC",
    ]:
        assert derive_rx(cls) is True, cls


def test_known_otc_classes_are_not_rx():
    for cls in [
        "COLD PRODUCTS",
        "MULTIVITAMIN",
        "ANTACID",
        "SKIN CARE",
        "ANALGESIC.ANTIPYRETIC",
        "ANTI-HISTAMINE.SECOND-GENERATION",
        # newly recovered from the previous "unknown -> Rx" bucket
        "COUGH PRODUCTS",
        "ANTISEPTIC",
        "MUCOLYTIC",
        "NASAL DECONGESTANT",
        "OMEGA 3",
    ]:
        assert derive_rx(cls) is False, cls


def test_hard_rx_list_always_wins():
    # An OTC-ish token combined with a prescription token must stay Rx.
    assert derive_rx("ANTINEOPLASTIC WITH VITAMIN SUPPORT") is True
    assert derive_rx("ANTI-HYPERTENSIVE.CALCIUM CHANNEL BLOCKER") is True
    assert derive_rx("PENICILLINS.MONOCOMPONENT") is True


def test_ambiguous_classes_stay_prescription():
    # Deliberately over-gated: not confidently OTC -> Rx.
    for cls in ["WEIGHT LOSS", "SEXUAL TONIC", "SLEEP AID", "FOLIC ACID DERIVATIVE"]:
        assert derive_rx(cls) is True, cls
