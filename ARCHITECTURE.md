# Food Recommendation System Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    User Input (CLI or API)                          │
│                  Origin Country → Destination Country               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Food Recommendation Orchestrator                    │
└───────┬─────────────────────────────────────────────────────┬───────┘
        │                                                     │
        ▼                                                     ▼
┌───────────────────┐                           ┌──────────────────────┐
│   AGENT 1         │                           │   AGENT 2            │
│ Origin Country    │                           │ Destination Country  │
│     Agent         │                           │     Agent            │
├───────────────────┤                           ├──────────────────────┤
│ Find destination  │                           │ Find popular dishes  │
│ dishes available  │                           │ in destination       │
│ in origin country │                           │ country              │
│ restaurants       │                           │                      │
└─────────┬─────────┘                           └──────────┬───────────┘
          │                                                │
          │  ["butter chicken",                           │  ["biryani",
          │   "tandoori chicken",                         │   "butter chicken",
          │   "naan",                                     │   "masala dosa",
          │   "samosa",                                   │   "samosa",
          │   "biryani", ...]                             │   "naan",
          │                                               │   "rogan josh",
          │                                               │   "pani puri", ...]
          │                                               │
          └──────────────────────┬────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      AGENT 3           │
                    │    Filter Agent        │
                    ├────────────────────────┤
                    │ 1. Set Difference:     │
                    │    Remove Agent1 dishes│
                    │    from Agent2 list    │
                    │                        │
                    │ 2. Rerank/Reweigh:     │
                    │    Boost scores of     │
                    │    unique dishes       │
                    │                        │
                    │ 3. Sort by score       │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  FILTERED RESULTS      │
                    │  ["masala dosa",       │
                    │   "rogan josh",        │
                    │   "pani puri",         │
                    │   "vada pav", ...]     │
                    │                        │
                    │  (Unique dishes that   │
                    │   are common in dest.  │
                    │   but rare in origin)  │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  TOP N RECOMMENDATIONS │
                    │  Ranked by adjusted    │
                    │  scores with strength  │
                    │  indicators            │
                    └────────────────────────┘
```

## Algorithm Details

### Step 1: Agent 1 - Origin Country Search
```
Input: destination_country="India", origin_country="USA"
Action: Search for Indian dishes available in US restaurants
Output: Set A = {butter chicken, tandoori chicken, naan, samosa, biryani, ...}
```

### Step 2: Agent 2 - Destination Country Search
```
Input: destination_country="India"
Action: Search for popular dishes in India
Output: Set B = {biryani, butter chicken, masala dosa, samosa, naan, 
                 rogan josh, pani puri, vada pav, ...}
```

### Step 3: Agent 3 - Set Difference & Reranking
```
Input: Set A (available in origin), Set B (popular in destination)
Action: 
  1. Compute C = B - A (dishes in destination but not in origin)
  2. For each dish in C:
       new_score = original_score * boost_factor
  3. Sort C by new_score (descending)
Output: Ranked list C = [(masala dosa, 141.0), (rogan josh, 114.0), ...]
```

## Example Execution

### USA → India (max=5, boost=1.5)

**Agent 1 Output** (10 dishes):
- butter chicken, chicken tikka masala, naan, samosa, tandoori chicken
- biryani, palak paneer, korma, vindaloo, dal makhani

**Agent 2 Output** (20 dishes):
- biryani, butter chicken, masala dosa, samosa, naan, tandoori chicken
- palak paneer, dal makhani, rogan josh, chole bhature, pani puri
- vada pav, idli, dhokla, hyderabadi biryani, chicken tikka masala
- aloo gobi, paneer tikka, korma, vindaloo

**Agent 3 Processing**:
- Remove: {butter chicken, tandoori chicken, naan, samosa, biryani, 
           palak paneer, korma, vindaloo, dal makhani, chicken tikka masala}
- Keep: {masala dosa, rogan josh, chole bhature, pani puri, vada pav, 
         idli, dhokla, hyderabadi biryani, aloo gobi, paneer tikka}
- Boost scores by 1.5x
- Sort by adjusted scores

**Final Output** (Top 5):
1. Masala Dosa (141.0) - Highly Recommended
2. Rogan Josh (114.0) - Worth Trying
3. Chole Bhature (109.5) - Worth Trying
4. Pani Puri (105.0) - Worth Trying
5. Vada Pav (100.5) - Worth Trying

## Scoring System

| Score Range | Recommendation Strength |
|-------------|------------------------|
| ≥ 140       | Highly Recommended     |
| 120-139     | Recommended            |
| 100-119     | Worth Trying           |
| < 100       | Consider               |

## Extensibility

The system is designed for easy extension:

1. **Add New Countries**: Update `COUNTRY_DISHES` and `DISHES_IN_COUNTRY_RESTAURANTS` in `search.py`
2. **Real Search APIs**: Replace `WebSearcher` methods with actual API calls (Google, Yelp, etc.)
3. **User Preferences**: Add dietary restrictions, spice levels, meal types
4. **Machine Learning**: Implement learning from user feedback to improve recommendations
5. **Regional Variations**: Support city/region-specific recommendations
