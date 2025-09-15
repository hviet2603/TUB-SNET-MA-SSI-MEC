credentials = {
    # edge operator alpha
    "did:indy:EeCGf1WF1dD7Sb8cDeEeq7": {
        "type": ["EdgeOperator"],
        "creds": {"name": "edge_operator_alpha"},
    },
    # edge operator beta
    "did:indy:CpJN2cuPHmzp5GvJv1Jh3y": {
        "type": ["EdgeOperator"],
        "creds": {"name": "edge_operator_beta"},
    },
    # car twin
    "did:indy:NFTSr3aVFrWkcXjh6jf3Ac": {
        "type": ["CarTwin"],
        "creds": {"name": "car_twin", "id": "car_twin_id_1", "car_id": "car_id_1"},
    },
    # drone twin
    "did:indy:4ZRTENo4kDF2mHb2xXct25": {
        "type": ["DroneTwin"],
        "creds": {
            "name": "drone_twin",
            "id": "drone_twin_id_1",
            "drone_id": "drone_id_1",
        },
    },
    # car
    "did:indy:U8KbaDYhfHRRP5AAVnkXtY": {
        "type": ["Car"],
        "creds": {"name": "car", "id": "car_id_1", "car_twin_id": "car_twin_id_1"},
    },
    # drone
    "did:indy:GV9zZYxygF5z9AvaDF8vdv": {
        "type": ["Drone"],
        "creds": {
            "name": "drone",
            "id": "drone_id_1",
            "drone_twin_id": "drone_twin_id_1",
        },
    },
}
