"""Calculate totals and ratios using aggregate numerators and denominators."""
MEASURES = ["spend", "clicks", "purchases", "revenue"]


def divide(numerator, denominator):
    return numerator / denominator if denominator else None


def totals(data):
    result = data[MEASURES].sum().to_dict()
    result.update(cpc=divide(result["spend"], result["clicks"]),
                  cost_per_purchase=divide(result["spend"], result["purchases"]),
                  roas=divide(result["revenue"], result["spend"]))
    return result


def summarize(data, dimensions):
    result = data.groupby(dimensions, as_index=False)[MEASURES].sum()
    result["cpc"] = result["spend"] / result["clicks"].where(result["clicks"].ne(0))
    result["cost_per_purchase"] = result["spend"] / result["purchases"].where(result["purchases"].ne(0))
    result["roas"] = result["revenue"] / result["spend"].where(result["spend"].ne(0))
    return result


def filter_data(data, start, end, campaigns, channels):
    return data.loc[data["date"].between(str(start), str(end))
                    & data["campaign_id"].isin(campaigns)
                    & data["channel"].isin(channels)].copy()
