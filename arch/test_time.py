from MarsClock.arch import marstime

bst_tests = [
    [(2024, 1, 1), False],
    [(2024, 1, 30), False],
    [(2024, 3, 15), False],
    [(2024, 3, 30), False],
    [(2024, 3, 31), True],
    [(2024, 4, 1), True],
    [(2024, 9, 30), True],
    [(2024, 10, 26), True],
    [(2024, 10, 27), False],
    [(2024, 12, 27), False],
    
    [(2025, 3, 29), False],
    [(2025, 3, 30), True],
    [(2025, 10, 25), True],
    [(2025, 10, 26), False],
    
    [(2026, 3, 28), False],
    [(2026, 3, 29), True],
    [(2026, 10, 24), True],
    [(2026, 10, 25), False],
]

for earth_dt, expected in bst_tests:
    actual = marstime.EarthCal.is_bst(earth_dt)
    if actual != expected:
        print(f"{earth_dt}, expected: {expected}, got: {actual}")
        
        

