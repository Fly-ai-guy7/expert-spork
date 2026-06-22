from collections import Counter


def compute_overview(sessions: list[dict]) -> dict:
    """Aggregate metrics across a list of training sessions.

    Each session dict carries: id, user_id, trainee_role, total_score,
    completed_at, coaching_report (the JSONB blob from
    TrainingSession.coaching_report). Pure function so it can be unit-tested
    without a database.
    """
    completed = [s for s in sessions if s.get("completed_at") is not None]
    scores = [s["total_score"] for s in completed if s.get("total_score") is not None]
    avg = (sum(scores) / len(scores)) if scores else 0.0

    grade_dist: Counter[str] = Counter()
    citation_counts: Counter[str] = Counter()
    pattern_counts: Counter[str] = Counter()
    council_alignments: list[str] = []
    needs_attention: list[dict] = []
    per_user_raw: dict[str, list[dict]] = {}

    for s in completed:
        report = s.get("coaching_report") or {}
        grade = report.get("grade")
        if grade:
            grade_dist[grade] += 1
        for c in report.get("missed_citations") or []:
            citation_counts[c] += 1
        for p in report.get("weak_patterns") or []:
            pattern_counts[p] += 1
        alignment = report.get("council_alignment")
        if alignment:
            council_alignments.append(alignment)
        per_user_raw.setdefault(s["user_id"], []).append(s)

        counsel_calls = report.get("counsel_calls_count") or 0
        if grade in ("D", "F") or alignment == "LOST" or counsel_calls > 5:
            needs_attention.append({
                "session_id": s["id"],
                "user_id": s["user_id"],
                "trainee_role": s["trainee_role"],
                "grade": grade,
                "total_score": s.get("total_score"),
                "council_alignment": alignment,
                "counsel_calls_count": counsel_calls,
                "completed_at": s.get("completed_at"),
            })

    per_user: list[dict] = []
    for uid, rows in per_user_raw.items():
        u_scores = [r["total_score"] for r in rows if r.get("total_score") is not None]
        rows_sorted = sorted(rows, key=lambda r: r["completed_at"])
        latest = rows_sorted[-1]
        per_user.append({
            "user_id": uid,
            "sessions": len(rows),
            "avg_score": (sum(u_scores) / len(u_scores)) if u_scores else 0.0,
            "latest_grade": (latest.get("coaching_report") or {}).get("grade"),
            "latest_completed_at": latest.get("completed_at"),
        })
    per_user.sort(key=lambda u: (-u["sessions"], u["user_id"]))

    council_lost = sum(1 for a in council_alignments if a == "LOST")
    council_lost_rate = (council_lost / len(council_alignments)) if council_alignments else None

    needs_attention.sort(key=lambda r: r["completed_at"], reverse=True)

    return {
        "total_sessions": len(sessions),
        "completed_sessions": len(completed),
        "avg_score": avg,
        "grade_distribution": dict(grade_dist),
        "per_user": per_user,
        "top_missed_citations": [
            {"citation": c, "count": n} for c, n in citation_counts.most_common(10)
        ],
        "top_weak_patterns": [
            {"pattern": p, "count": n} for p, n in pattern_counts.most_common(5)
        ],
        "council_lost_rate": council_lost_rate,
        "needs_attention": needs_attention,
    }
