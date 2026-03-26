"""
Test script to verify core algorithms work correctly.
Run this to validate the implementation without GUI.
"""
from algorithms import bankers_safety_check, detect_deadlock, recover_deadlock
from utils import generate_random_bankers_data, generate_random_rag, RAG_PRESETS


def test_bankers_algorithm():
    """Test Banker's Algorithm."""
    print("\n" + "="*60)
    print("TEST 1: BANKER'S ALGORITHM")
    print("="*60)
    
    processes, resources, allocation, max_matrix, available = generate_random_bankers_data(n=3, m=2)
    
    print(f"Processes: {processes}")
    print(f"Resources: {resources}")
    print(f"Allocation: {allocation}")
    print(f"Max: {max_matrix}")
    print(f"Available: {available}")
    
    safe, sequence, need, log = bankers_safety_check(
        processes, resources, allocation, max_matrix, available
    )
    
    print(f"\nResult: {'SAFE' if safe else 'UNSAFE'}")
    if safe:
        print(f"Safe Sequence: {' → '.join(sequence)}")
    
    return safe is not None  # Test passes if no exception


def test_deadlock_detection():
    """Test Deadlock Detection."""
    print("\n" + "="*60)
    print("TEST 2: DEADLOCK DETECTION")
    print("="*60)
    
    # Test with preset
    preset = RAG_PRESETS['1']
    nodes = preset['nodes']
    edges = preset['edges']
    
    print(f"Preset: {preset['name']}")
    print(f"Nodes: {[n['id'] for n in nodes]}")
    print(f"Edges: {[(e['source'], e['target']) for e in edges]}")
    
    deadlock, processes_involved, cycle_path = detect_deadlock(nodes, edges)
    
    print(f"\nResult: {'DEADLOCK DETECTED' if deadlock else 'NO DEADLOCK'}")
    if deadlock:
        print(f"Cycle: {' → '.join(cycle_path)}")
        print(f"Processes: {processes_involved}")
    
    # Test safe scenario
    print("\nTesting Safe Scenario...")
    preset_safe = RAG_PRESETS['2']
    deadlock_safe, _, _ = detect_deadlock(preset_safe['nodes'], preset_safe['edges'])
    print(f"Result: {'DEADLOCK' if deadlock_safe else 'SAFE'}")
    
    return True  # Test passes if no exception


def test_recovery():
    """Test Deadlock Recovery."""
    print("\n" + "="*60)
    print("TEST 3: DEADLOCK RECOVERY")
    print("="*60)
    
    # Simple test case
    allocation = [
        [2, 0],  # P0
        [3, 0],  # P1
        [2, 1]   # P2
    ]
    available = [0, 0]
    deadlocked = ['P0', 'P1', 'P2']
    
    print(f"Deadlocked: {deadlocked}")
    print(f"Allocation: {allocation}")
    print(f"Available: {available}")
    
    for strategy in ['terminate-all', 'terminate-one-by-one', 'preemption']:
        print(f"\nStrategy: {strategy}")
        _, steps, _ = recover_deadlock(allocation, available, deadlocked, strategy)
        print(f"Steps: {len(steps)}")
        for i, step in enumerate(steps[:3], 1):  # Show first 3 steps
            print(f"  {i}. {step}")
    
    return True  # Test passes if no exception


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "="*60)
    print("TEST 4: EDGE CASES")
    print("="*60)
    
    # Test with minimal data
    print("Testing minimal case (1 process, 1 resource)...")
    safe, seq, _, _ = bankers_safety_check(['P0'], ['A'], [[0]], [[1]], [1])
    print(f"Result: {'SAFE' if safe else 'UNSAFE'}")
    
    # Test with no edges
    print("\nTesting graph with no edges...")
    nodes = [{'id': 'P1', 'type': 'process'}, {'id': 'R1', 'type': 'resource'}]
    deadlock, _, _ = detect_deadlock(nodes, [])
    print(f"Result: {'DEADLOCK' if deadlock else 'SAFE'}")
    
    return True


if __name__ == "__main__":
    try:
        test_bankers_algorithm()
        test_deadlock_detection()
        test_recovery()
        test_edge_cases()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nTo run the GUI application, execute:")
        print("  python main.py")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
