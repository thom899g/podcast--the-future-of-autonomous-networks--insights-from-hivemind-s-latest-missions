"""
Podcast Episode Generator - Autonomous System for Episode 50
Mission: Generate and publish Episode 50 on autonomous networks with HiveMind insights
Author: World-Class Autonomous Architect
Date: 2024
"""

import logging
import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
import os
from pathlib import Path
import sys

# Configure logging for ecosystem tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@dataclass
class PodcastEpisode:
    """Data class representing a podcast episode with validation"""
    episode_number: int
    title: str
    hook: str
    description: str
    tags: List[str]
    script: str
    host: str = "HiveMind Autonomous Network"
    duration_minutes: int = 45
    publish_date: Optional[str] = None
    status: str = "draft"
    
    def __post_init__(self):
        """Validate episode data after initialization"""
        self.validate()
        if not self.publish_date:
            self.publish_date = datetime.datetime.now().isoformat()
    
    def validate(self) -> None:
        """Validate all episode fields with comprehensive error handling"""
        validation_errors = []
        
        if not isinstance(self.episode_number, int) or self.episode_number <= 0:
            validation_errors.append("Episode number must be a positive integer")
        
        if not isinstance(self.title, str) or len(self.title.strip()) < 10:
            validation_errors.append("Title must be a string with at least 10 characters")
        
        if not isinstance(self.hook, str) or len(self.hook.strip()) < 50:
            validation_errors.append("Hook must be a descriptive string with at least 50 characters")
        
        if not isinstance(self.tags, list) or len(self.tags) < 3:
            validation_errors.append("Must provide at least 3 tags")
        
        if validation_errors:
            error_msg = f"Validation failed: {', '.join(validation_errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def to_dict(self) -> Dict:
        """Convert episode to dictionary for Firestore storage"""
        return {
            **asdict(self),
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }

class PodcastEpisodeGenerator:
    """Main generator class for creating and publishing podcast episodes"""
    
    def __init__(self, firebase_credentials_path: Optional[str] = None):
        """Initialize generator with Firebase connection"""
        self.firestore_client = None
        self.initialized = False
        self._initialize_firebase(firebase_credentials_path)
        
    def _initialize_firebase(self, credentials_path: Optional[str]) -> None:
        """Initialize Firebase connection with error handling"""
        try:
            if firebase_admin._apps:
                # Firebase already initialized
                self.firestore_client = firestore.client()
                self.initialized = True
                logger.info("Firebase already initialized, using existing connection")
                return
            
            # Check for credentials
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                logger.info(f"Using Firebase credentials from: {credentials_path}")
            else:
                # Try environment variable
                cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
                if cred_json:
                    cred_dict = json.loads(cred_json)
                    cred = credentials.Certificate(cred_dict)
                    logger.info("Using Firebase credentials from environment variable")
                else:
                    # Try default location
                    default_path = "serviceAccountKey.json"
                    if os.path.exists(default_path):
                        cred = credentials.Certificate(default_path)
                        logger.info(f"Using Firebase credentials from default path: {default_path}")
                    else:
                        logger.warning("No Firebase credentials found. Operating in local mode only.")
                        self.initialized = False
                        return
            
            # Initialize Firebase
            firebase_admin.initialize_app(cred)
            self.firestore_client = firestore.client()
            self.initialized = True
            logger.info("Firebase initialized successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Firebase credentials file not found: {e}")
            self.initialized = False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in Firebase credentials: {e}")
            self.initialized = False
        except ValueError as e:
            logger.error(f"Invalid Firebase credentials: {e}")
            self.initialized = False
        except FirebaseError as e:
            logger.error(f"Firebase initialization error: {e}")
            self.initialized = False
        except Exception as e:
            logger.error(f"Unexpected error during Firebase initialization: {e}")
            self.initialized = False
    
    def generate_