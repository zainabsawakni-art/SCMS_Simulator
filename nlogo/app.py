"""
Flask application for Credit Insurance and Rating System Simulation.
Replication of NetLogo CIES 9.1 Model
"""
from flask import Flask, render_template, jsonify, request
from simulation.world import World
import threading
import time

app = Flask(__name__)

# Disable template caching for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Global simulation instance
world = World()
simulation_thread = None
simulation_running = False
simulation_lock = threading.Lock()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup():
    """Initialize the simulation with parameters."""
    global world, simulation_running
    
    try:
        with simulation_lock:
            simulation_running = False
            time.sleep(0.1)  # Allow any running thread to stop
            
            # Get parameters from request
            params = request.json or {}
            
            # Update world parameters if provided
            if 'world_size' in params:
                world.world_size = int(params['world_size'])
            if 'base_rate' in params:
                world.base_rate = float(params['base_rate'])
            if 'premium_increment' in params:
                world.premium_increment = float(params['premium_increment'])
            if 'min_installment' in params:
                world.min_installment = float(params['min_installment'])
            if 'max_installment' in params:
                world.max_installment = float(params['max_installment'])
            if 'min_periods' in params:
                world.min_periods = int(params['min_periods'])
            if 'max_periods' in params:
                world.max_periods = int(params['max_periods'])
            if 'no_of_periods' in params:
                world.no_of_periods = int(params['no_of_periods'])
            if 'insolvency_risk' in params:
                world.insolvency_risk = float(params['insolvency_risk'])
            if 'unpaid_fraction' in params:
                world.unpaid_fraction = float(params['unpaid_fraction'])
            if 'max_day' in params:
                world.max_day = int(params['max_day'])
            if 'peer_effect' in params:
                world.peer_effect = float(params['peer_effect'])
            if 'reserve_ratio' in params:
                world.reserve_ratio = float(params['reserve_ratio'])
            if 'compensation_ratio' in params:
                world.compensation_ratio = float(params['compensation_ratio'])
            if 'randomness' in params:
                world.randomness = float(params['randomness'])
            if 'renew_financing' in params:
                world.renew_financing = bool(params['renew_financing'])
            if 'incentive_system' in params:
                world.incentive_system = bool(params['incentive_system'])
            if 'adjust_compensation' in params:
                world.adjust_compensation = bool(params['adjust_compensation'])
            if 'fix_random_seed' in params:
                world.fix_random_seed = bool(params['fix_random_seed'])
            if 'seed_number' in params and world.fix_random_seed:
                world.set_random_seed(int(params['seed_number']))
            
            # Setup simulation
            world.setup()
            
            return jsonify({
                'success': True,
                'message': 'Simulation initialized successfully',
                'state': world.get_state()
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/step', methods=['POST'])
def step():
    """Execute a single simulation step."""
    global world
    
    try:
        with simulation_lock:
            if world.month == 0:
                return jsonify({
                    'success': False,
                    'message': 'Please setup the simulation first'
                }), 400
            
            can_continue = world.step()
            state = world.get_state()
            
            return jsonify({
                'success': True,
                'can_continue': can_continue,
                'state': state
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/go', methods=['POST'])
def go():
    """Start continuous simulation."""
    global simulation_running, simulation_thread
    
    with simulation_lock:
        if world.month == 0:
            return jsonify({
                'success': False,
                'message': 'Please setup the simulation first'
            }), 400
        
        if simulation_running:
            return jsonify({
                'success': False,
                'message': 'Simulation is already running'
            }), 400
        
        simulation_running = True
    
    return jsonify({'success': True, 'message': 'Simulation started'})

@app.route('/api/stop', methods=['POST'])
def stop():
    """Stop continuous simulation."""
    global simulation_running
    
    with simulation_lock:
        simulation_running = False
    
    return jsonify({'success': True, 'message': 'Simulation stopped'})

@app.route('/api/is_running', methods=['GET'])
def is_running():
    """Check if simulation is running."""
    return jsonify({'running': simulation_running})

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current simulation state."""
    try:
        with simulation_lock:
            if world.month == 0:
                return jsonify({
                    'success': False,
                    'message': 'Simulation not initialized'
                }), 400
            
            state = world.get_state()
            return jsonify({
                'success': True,
                'state': state
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    """Get current simulation parameters."""
    return jsonify({
        'world_size': world.world_size,
        'base_rate': world.base_rate,
        'premium_increment': world.premium_increment,
        'min_installment': world.min_installment,
        'max_installment': world.max_installment,
        'min_periods': world.min_periods,
        'max_periods': world.max_periods,
        'no_of_periods': world.no_of_periods,
        'insolvency_risk': world.insolvency_risk,
        'unpaid_fraction': world.unpaid_fraction,
        'max_day': world.max_day,
        'p_day_response': world.p_day_response,
        'premium_response': world.premium_response,
        'peer_effect': world.peer_effect,
        'reserve_ratio': world.reserve_ratio,
        'compensation_ratio': world.compensation_ratio,
        'randomness': world.randomness,
        'renew_financing': world.renew_financing,
        'incentive_system': world.incentive_system,
        'adjust_compensation': world.adjust_compensation,
        'fix_random_seed': world.fix_random_seed,
        'seed_number': world.seed_number
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
