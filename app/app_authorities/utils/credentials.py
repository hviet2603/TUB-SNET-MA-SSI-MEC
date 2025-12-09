from ...global_config import DID_PREFIX

credentials = {
    # edge alpha
    f"{DID_PREFIX}LFrSJFNqGcfUZk11LCwbfJ": {
        "type": ["Edge"],
        "creds": {"name": "edge_alpha"},
    },
    # edge beta
    f"{DID_PREFIX}W4AapQQq2xsufNJuYf58VQ": {
        "type": ["Edge"],
        "creds": {"name": "edge_beta"},
    },
    # car twin
    f"{DID_PREFIX}NFTSr3aVFrWkcXjh6jf3Ac": {
        "type": ["CarTwin"],
        "creds": {
            "name": "car_twin",
            "car_twin_id": "car_twin_id_1",
            "car_id": "car_id_1",
        },
    },
    # drone twin
    f"{DID_PREFIX}4ZRTENo4kDF2mHb2xXct25": {
        "type": ["DroneTwin"],
        "creds": {
            "name": "drone_twin",
            "drone_twin_id": "drone_twin_id_1",
            "drone_id": "drone_id_1",
        },
    },
    # car
    f"{DID_PREFIX}U8KbaDYhfHRRP5AAVnkXtY": {
        "type": ["Car"],
        "creds": {"name": "car", "car_id": "car_id_1", "car_twin_id": "car_twin_id_1"},
    },
    # drone
    f"{DID_PREFIX}GV9zZYxygF5z9AvaDF8vdv": {
        "type": ["Drone"],
        "creds": {
            "name": "drone",
            "drone_id": "drone_id_1",
            "drone_twin_id": "drone_twin_id_1",
        },
    },
}
