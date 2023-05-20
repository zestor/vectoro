import numpy as np
from sklearn.linear_model import LinearRegression

def predict_time(performance_timings, future_record_count):
    # Extract record counts and times from performance timings
    record_counts = np.array([timing[0] for timing in performance_timings]).reshape(-1, 1)
    times = np.array([timing[1] for timing in performance_timings])

    # Train a linear regression model on the given data
    model = LinearRegression()
    model.fit(record_counts, times)

    # Predict the time for the future higher number of records
    future_time = model.predict(np.array([[future_record_count]]))

    return future_time[0]

# Example usage
performance_timings = [
    (1000, 0.03),
    (10000, 0.17),
    (100000, 1.0),
    (1000000, 9.610676),
]

future_record_count = 1000000
predicted_time = predict_time(performance_timings, future_record_count)
print(f"Predicted time for {future_record_count} records: {predicted_time} seconds")
