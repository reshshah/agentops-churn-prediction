import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime

fake = Faker()
np.random.seed(42)


def generate_member_cohort(n: int = 10_000) -> pd.DataFrame:
    """Generate synthetic member behavioral data with churn signal embedded
    in behavioral decay patterns. ~15% churn rate."""
    now = datetime.utcnow()
    records = []

    for _ in range(n):
        will_churn = np.random.random() < 0.15
        decay = np.random.uniform(0.3, 0.8) if will_churn else np.random.uniform(0.85, 1.1)
        baseline_app_opens = np.random.poisson(lam=12)

        records.append({
            "member_id": f"M-{fake.unique.random_int(min=10000, max=99999)}",
            "tenure_days": np.random.randint(30, 1200),
            "renewal_days_remaining": np.random.randint(1, 90),
            "segment": np.random.choice(
                ["grocery_heavy", "convenience", "price_sensitive", "mixed"]
            ),

            # Behavioral signals — decayed for churners
            "app_opens_7d": max(0, int(baseline_app_opens * decay + np.random.normal(0, 1))),
            "app_opens_30d_baseline": baseline_app_opens * 4,
            "basket_refill_rate": round(np.clip(np.random.normal(0.7, 0.15) * decay, 0, 1), 3),
            "session_duration_minutes": round(max(0, np.random.exponential(8) * decay), 1),
            "free_shipping_utilization": round(np.clip(np.random.normal(0.6, 0.2), 0, 1), 3),
            "nudge_skips_30d": (
                np.random.choice([0, 1, 2, 3, 4], p=[0.5, 0.2, 0.15, 0.1, 0.05])
                if will_churn
                else np.random.choice([0, 1], p=[0.85, 0.15])
            ),
            "category_breadth": max(
                1, int(np.random.normal(5, 2) * (1 if not will_churn else decay))
            ),
            "pickup_to_delivery_shift": round(
                np.random.uniform(0, 0.4) * (2 if will_churn else 1), 3
            ),

            # Ground truth — training only, never passed to model at inference
            "churned_within_60d": int(will_churn),
            "generated_at": now.isoformat(),
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df = generate_member_cohort(10_000)
    df.to_csv("data/synthetic/members.csv", index=False)
    print(f"Generated {len(df)} members. Churn rate: {df.churned_within_60d.mean():.1%}")
