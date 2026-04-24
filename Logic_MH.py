# SECTION 1: IMPORTS & FLASK SETUP
from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)


# SECTION 2: LOGIC ENGINE + MATHEMATICAL MODELING

def estimate_emergency_probability(emergency_signal_strength):
    return 1 / (1 + math.exp(-emergency_signal_strength))


def expected_traffic_delay(vehicles, accident_prob):
    base_delay = vehicles * 2
    risk_delay = accident_prob * 20
    return base_delay + risk_delay


def evaluate_direction(vehicle_count, emergency_active, road_closed, threshold=10):
    P1 = vehicle_count > threshold
    P2 = emergency_active
    P3 = road_closed

    premise_is_true = P1 and not P2 and not P3

    if premise_is_true:
        return "GREEN"
    else:
        return "RED"


def evaluate_intersection(data, threshold=10):
    results = {}
    for direction, info in data.items():
        status = evaluate_direction(
            info["vehicles"],
            info["emergency"],
            info["road_closed"],
            threshold
        )
        results[direction] = status
    return results


def calculate_priority_score(vehicles, wait_time, accident_prob, w=None):
    if w is None:
        w = [1.0, 1.5, 2.0]

    feature_vector = [vehicles, wait_time, accident_prob]
    score = sum(f * weight for f, weight in zip(feature_vector, w))
    return score


def resolve_conflict(data, logic_states):
    highest_score = -1
    winning_direction = None

    for direction, state in logic_states.items():
        if state == "GREEN":
            v = data[direction]["vehicles"]
            t = data[direction]["wait_time"]

            emergency_signal = data[direction].get("emergency_signal", 0)
            accident_prob = estimate_emergency_probability(emergency_signal)

            score = calculate_priority_score(v, t, accident_prob)
            delay_risk = expected_traffic_delay(v, accident_prob)
            final_score = score + delay_risk

            if final_score > highest_score:
                highest_score = final_score
                winning_direction = direction

    return winning_direction


# SECTION 3: THE API ROUTE (THE LISTENER)
@app.route('/api/evaluate', methods=['POST'])
def process_traffic():
    incoming_data = request.json

    valid_directions = evaluate_intersection(incoming_data, threshold=10)
    final_green_light = resolve_conflict(incoming_data, valid_directions)

    final_states = {}
    for direction in incoming_data.keys():
        if direction == final_green_light:
            final_states[direction] = "GREEN"
        else:
            final_states[direction] = "RED"

    return jsonify(final_states)


# SECTION 4: THE SERVER TRIGGER
if __name__ == '__main__':
    app.run(debug=True, port=5000)