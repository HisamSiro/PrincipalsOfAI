# SECTION 1: IMPORTS & FLASK SETUP
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 


# SECTION 2: YOUR COLAB FUNCTIONS (THE BRAIN)
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

def calculate_priority_score(vehicles, wait_time, w1=1.0, w2=1.5):
    return (w1 * vehicles) + (w2 * wait_time)

def resolve_conflict(data, logic_states):
    highest_score = -1
    winning_direction = None
    
    for direction, state in logic_states.items():
        if state == "GREEN":
            v = data[direction]["vehicles"]
            t = data[direction]["wait_time"] # Make sure the UI sends 'wait_time' in the JSON!
            score = calculate_priority_score(v, t)
            
            if score > highest_score:
                highest_score = score
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