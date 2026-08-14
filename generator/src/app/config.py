class Settings():
    PROJECT_NAME: str = "Synthetic Data & Chaos Engine"
    DESCRIPTION: str = "Engine for generating clean and mutated pension member datasets for pipeline testing."
    API_V1_STR: str = "/api/v1"
    
    
    # Default Chaos Probabilities
    DEFAULT_NULL_RATE: float = 0.03
    DEFAULT_DRIFT_RATE: float = 0.05