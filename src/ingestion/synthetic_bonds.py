from __future__ import annotations
import random
from datetime import date, timedelta

RATINGS = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']
SECTORS = ['Technology', 'Energy', 'Financial', 'Healthcare', 'Consumer']
AGENCIES = ['Moodys', 'SP', 'Fitch']

def generate_bonds(n: int) -> list:
    bonds = []
    for i in range(1, n + 1):
        bonds.append({
            'bond_id': i,
            'isin': f'US{i:09d}',
            'issuer': f'Company_{i}',
            'sector': random.choice(SECTORS),        # ¿qué lista?
            'issue_date': date(2020, 1, 1) + timedelta(days=random.randint(0, 365)),
            'maturity_date': date(2028, 1, 1) + timedelta(days=random.randint(0, 730)),
            'coupon_rate': round(random.uniform(2.0, 8.0), 2),
            'face_value': random.choice([1000, 5000, 10000]),
        })
    return bonds

def generate_ratings(bonds: list) -> list:
    ratings = []
    for bond in bonds:
        # cada bono empieza con un rating inicial
        current_rating_idx = random.randint(0, 4)  # entre AAA y BB
        effective_date = bond['issue_date']
        
        # genera entre 1 y 3 cambios de rating
        for _ in range(random.randint(1, 3)):
            ratings.append({
                'bond_id': bond['bond_id'],
                'agency': random.choice(AGENCIES),
                'rating': RATINGS[current_rating_idx],
                'effective_date': effective_date,
            })
            # mueve el rating un escalón arriba o abajo
            current_rating_idx = max(0, min(6, current_rating_idx + random.choice([-1, 1])))
            effective_date = effective_date + timedelta(days=random.randint(90, 365))
    
    return ratings