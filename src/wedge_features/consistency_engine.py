"""
Consistency Engine with Reference Management - Wedge Feature #3

Solves critical pain point of cross-shot consistency that competitors struggle with.
Maintains character identity, lighting, spatial relationships across scenes.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from datetime import datetime
import pickle
import cv2


class ConsistencyType(Enum):
    """Types of consistency to maintain"""

    CHARACTER_IDENTITY = "character_identity"
    LIGHTING = "lighting"
    COLOR_GRADING = "color_grading"
    SPATIAL_RELATIONSHIP = "spatial_relationship"
    OBJECT_APPEARANCE = "object_appearance"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"
    STYLE = "style"
    WORLD = "world"


@dataclass
class StyleAnchor:
    """Style reference anchor for consistent artistic direction"""

    anchor_id: str
    name: str
    description: str
    style_embedding: np.ndarray
    visual_attributes: Dict[str, Any] = field(default_factory=dict)
    color_palette: List[Tuple[int, int, int]] = field(default_factory=list)
    texture_profile: Optional[Dict] = None
    lighting_style: Optional[Dict] = None
    composition_rules: List[str] = field(default_factory=list)
    reference_images: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["style_embedding"] = self.style_embedding.tolist()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "StyleAnchor":
        """Create from dictionary"""
        data["style_embedding"] = np.array(data["style_embedding"])
        return cls(**data)


@dataclass
class CharacterReference:
    """Character reference for identity preservation"""

    character_id: str
    name: str
    description: str
    appearance_embedding: np.ndarray
    facial_features: Dict[str, Any] = field(default_factory=dict)
    body_proportions: Dict[str, float] = field(default_factory=dict)
    clothing: Dict[str, Any] = field(default_factory=dict)
    color_scheme: List[Tuple[int, int, int]] = field(default_factory=list)
    distinctive_marks: List[str] = field(default_factory=list)
    reference_images: List[str] = field(default_factory=list)
    expression_variants: Dict[str, np.ndarray] = field(default_factory=dict)
    pose_variants: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["appearance_embedding"] = self.appearance_embedding.tolist()
        data["expression_variants"] = {k: v.tolist() for k, v in self.expression_variants.items()}
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterReference":
        """Create from dictionary"""
        data["appearance_embedding"] = np.array(data["appearance_embedding"])
        data["expression_variants"] = {k: np.array(v) for k, v in data.get("expression_variants", {}).items()}
        return cls(**data)


@dataclass
class WorldReference:
    """World/environment reference for spatial consistency"""

    world_id: str
    name: str
    description: str
    spatial_embedding: np.ndarray
    location_map: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)
    lighting_conditions: Dict[str, Any] = field(default_factory=dict)
    time_of_day: Optional[str] = None
    weather: Optional[str] = None
    architectural_style: Optional[str] = None
    scale_references: Dict[str, float] = field(default_factory=dict)
    reference_images: List[str] = field(default_factory=list)
    spatial_relationships: Dict[str, List[str]] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["spatial_embedding"] = self.spatial_embedding.tolist()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "WorldReference":
        """Create from dictionary"""
        data["spatial_embedding"] = np.array(data["spatial_embedding"])
        return cls(**data)


@dataclass
class ReferenceFrame:
    """Reference frame for consistency checking"""

    frame_id: str
    shot_id: str
    timestamp: float
    embeddings: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    color_histogram: Optional[np.ndarray] = None
    lighting_profile: Optional[Dict] = None
    character_positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    object_registry: Dict[str, Any] = field(default_factory=dict)
    style_anchor_id: Optional[str] = None
    character_ids: Set[str] = field(default_factory=set)
    world_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = {
            "frame_id": self.frame_id,
            "shot_id": self.shot_id,
            "timestamp": self.timestamp,
            "embeddings": {k: v.tolist() for k, v in self.embeddings.items()},
            "metadata": self.metadata,
            "color_histogram": self.color_histogram.tolist() if self.color_histogram is not None else None,
            "lighting_profile": self.lighting_profile,
            "character_positions": {k: list(v) for k, v in self.character_positions.items()},
            "object_registry": self.object_registry,
            "style_anchor_id": self.style_anchor_id,
            "character_ids": list(self.character_ids),
            "world_id": self.world_id,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "ReferenceFrame":
        """Create from dictionary"""
        data["embeddings"] = {k: np.array(v) for k, v in data.get("embeddings", {}).items()}
        if data.get("color_histogram"):
            data["color_histogram"] = np.array(data["color_histogram"])
        data["character_positions"] = {k: tuple(v) for k, v in data.get("character_positions", {}).items()}
        data["character_ids"] = set(data.get("character_ids", []))
        return cls(**data)


@dataclass
class ConsistencyViolation:
    """Detected consistency violation"""

    violation_type: ConsistencyType
    severity: float
    description: str
    frame_a: str
    frame_b: str
    suggested_fix: str
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContinuityRule:
    """Rule for maintaining continuity across shots"""

    rule_id: str
    rule_type: ConsistencyType
    name: str
    description: str
    threshold: float
    enabled: bool = True
    weight: float = 1.0
    conditions: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, frame_a: ReferenceFrame, frame_b: ReferenceFrame) -> Optional[float]:
        """Evaluate rule compliance, returns score 0-1 or None if not applicable"""
        raise NotImplementedError("Subclasses must implement evaluate method")


class ColorConsistencyRule(ContinuityRule):
    """Rule for color consistency across shots"""

    def __init__(self, threshold: float = 0.1, **kwargs):
        super().__init__(
            rule_id="color_consistency",
            rule_type=ConsistencyType.COLOR_GRADING,
            name="Color Consistency",
            description="Maintains consistent color grading across shots",
            threshold=threshold,
            **kwargs,
        )

    def evaluate(self, frame_a: ReferenceFrame, frame_b: ReferenceFrame) -> Optional[float]:
        """Evaluate color consistency"""
        if frame_a.color_histogram is None or frame_b.color_histogram is None:
            return None

        diff = np.mean(np.abs(frame_a.color_histogram - frame_b.color_histogram))
        return 1.0 - min(diff, 1.0)


class LightingContinuityRule(ContinuityRule):
    """Rule for lighting continuity"""

    def __init__(self, threshold: float = 0.15, **kwargs):
        super().__init__(
            rule_id="lighting_continuity",
            rule_type=ConsistencyType.LIGHTING,
            name="Lighting Continuity",
            description="Maintains consistent lighting across shots",
            threshold=threshold,
            **kwargs,
        )

    def evaluate(self, frame_a: ReferenceFrame, frame_b: ReferenceFrame) -> Optional[float]:
        """Evaluate lighting continuity"""
        if not frame_a.lighting_profile or not frame_b.lighting_profile:
            return None

        intensity_diff = abs(
            frame_a.lighting_profile.get("intensity", 0) - frame_b.lighting_profile.get("intensity", 0)
        )

        color_temp_diff = (
            abs(
                frame_a.lighting_profile.get("color_temperature", 5500)
                - frame_b.lighting_profile.get("color_temperature", 5500)
            )
            / 5000.0
        )

        score = 1.0 - (intensity_diff + color_temp_diff) / 2.0
        return max(0.0, min(1.0, score))


class SpatialCoherenceRule(ContinuityRule):
    """Rule for spatial coherence"""

    def __init__(self, threshold: float = 0.2, **kwargs):
        super().__init__(
            rule_id="spatial_coherence",
            rule_type=ConsistencyType.SPATIAL_RELATIONSHIP,
            name="Spatial Coherence",
            description="Maintains consistent spatial relationships",
            threshold=threshold,
            **kwargs,
        )

    def evaluate(self, frame_a: ReferenceFrame, frame_b: ReferenceFrame) -> Optional[float]:
        """Evaluate spatial coherence"""
        common_objects = set(frame_a.character_positions.keys()) & set(frame_b.character_positions.keys())

        if not common_objects:
            return None

        total_score = 0.0
        for obj_id in common_objects:
            pos_a = frame_a.character_positions[obj_id]
            pos_b = frame_b.character_positions[obj_id]
            distance = np.sqrt((pos_a[0] - pos_b[0]) ** 2 + (pos_a[1] - pos_b[1]) ** 2)
            obj_score = 1.0 - min(distance, 1.0)
            total_score += obj_score

        return total_score / len(common_objects)


class ReferenceLibrary:
    """
    Storage and management of reference library

    Organizes and persists:
    - Character references
    - Style anchors
    - World/environment references
    - Reference frames
    """

    def __init__(self, storage_path: str = "data/reference_library"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        self.characters_dir = self.storage_path / "characters"
        self.styles_dir = self.storage_path / "styles"
        self.worlds_dir = self.storage_path / "worlds"
        self.frames_dir = self.storage_path / "frames"

        for directory in [self.characters_dir, self.styles_dir, self.worlds_dir, self.frames_dir]:
            directory.mkdir(exist_ok=True)

        self.characters: Dict[str, CharacterReference] = {}
        self.styles: Dict[str, StyleAnchor] = {}
        self.worlds: Dict[str, WorldReference] = {}
        self.frames: Dict[str, ReferenceFrame] = {}

        self._load_all_references()

    def _load_all_references(self):
        """Load all references from disk"""
        try:
            for char_file in self.characters_dir.glob("*.json"):
                with open(char_file, "r") as f:
                    data = json.load(f)
                    char = CharacterReference.from_dict(data)
                    self.characters[char.character_id] = char

            for style_file in self.styles_dir.glob("*.json"):
                with open(style_file, "r") as f:
                    data = json.load(f)
                    style = StyleAnchor.from_dict(data)
                    self.styles[style.anchor_id] = style

            for world_file in self.worlds_dir.glob("*.json"):
                with open(world_file, "r") as f:
                    data = json.load(f)
                    world = WorldReference.from_dict(data)
                    self.worlds[world.world_id] = world

            self.logger.info(
                f"Loaded {len(self.characters)} characters, " f"{len(self.styles)} styles, {len(self.worlds)} worlds"
            )
        except Exception as e:
            self.logger.error(f"Error loading references: {e}")

    def add_character(self, character: CharacterReference) -> bool:
        """Add character reference to library"""
        try:
            self.characters[character.character_id] = character
            char_file = self.characters_dir / f"{character.character_id}.json"
            with open(char_file, "w") as f:
                json.dump(character.to_dict(), f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error adding character: {e}")
            return False

    def add_style_anchor(self, style: StyleAnchor) -> bool:
        """Add style anchor to library"""
        try:
            self.styles[style.anchor_id] = style
            style_file = self.styles_dir / f"{style.anchor_id}.json"
            with open(style_file, "w") as f:
                json.dump(style.to_dict(), f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error adding style anchor: {e}")
            return False

    def add_world(self, world: WorldReference) -> bool:
        """Add world reference to library"""
        try:
            self.worlds[world.world_id] = world
            world_file = self.worlds_dir / f"{world.world_id}.json"
            with open(world_file, "w") as f:
                json.dump(world.to_dict(), f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error adding world: {e}")
            return False

    def add_frame(self, frame: ReferenceFrame) -> bool:
        """Add reference frame to library"""
        try:
            self.frames[frame.frame_id] = frame
            frame_file = self.frames_dir / f"{frame.frame_id}.pkl"
            with open(frame_file, "wb") as f:
                pickle.dump(frame, f)
            return True
        except Exception as e:
            self.logger.error(f"Error adding frame: {e}")
            return False

    def get_character(self, character_id: str) -> Optional[CharacterReference]:
        """Retrieve character reference"""
        return self.characters.get(character_id)

    def get_style(self, anchor_id: str) -> Optional[StyleAnchor]:
        """Retrieve style anchor"""
        return self.styles.get(anchor_id)

    def get_world(self, world_id: str) -> Optional[WorldReference]:
        """Retrieve world reference"""
        return self.worlds.get(world_id)

    def get_frame(self, frame_id: str) -> Optional[ReferenceFrame]:
        """Retrieve reference frame"""
        if frame_id in self.frames:
            return self.frames[frame_id]

        frame_file = self.frames_dir / f"{frame_id}.pkl"
        if frame_file.exists():
            try:
                with open(frame_file, "rb") as f:
                    frame = pickle.load(f)
                    self.frames[frame_id] = frame
                    return frame
            except Exception as e:
                self.logger.error(f"Error loading frame: {e}")

        return None

    def find_similar_characters(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar characters by embedding"""
        similarities = []
        for char_id, char in self.characters.items():
            similarity = self._cosine_similarity(query_embedding, char.appearance_embedding)
            similarities.append((char_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def find_similar_styles(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar styles by embedding"""
        similarities = []
        for style_id, style in self.styles.items():
            similarity = self._cosine_similarity(query_embedding, style.style_embedding)
            similarities.append((style_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def export_library(self, export_path: str) -> bool:
        """Export entire library to archive"""
        try:
            import tarfile

            export_path = Path(export_path)

            with tarfile.open(export_path, "w:gz") as tar:
                tar.add(self.storage_path, arcname="reference_library")

            self.logger.info(f"Library exported to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting library: {e}")
            return False


class ReferenceManager:
    """
    Manages reference frames for consistency checking

    Stores and retrieves reference images/embeddings for:
    - Character appearances
    - Lighting setups
    - Spatial layouts
    - Object continuity
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or "data/reference_library"
        self.references: Dict[str, ReferenceFrame] = {}
        self.character_library: Dict[str, List[str]] = {}
        self.object_library: Dict[str, List[str]] = {}

        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    def add_reference(self, frame: ReferenceFrame, tags: Optional[List[str]] = None) -> bool:
        """Add a new reference frame"""
        try:
            self.references[frame.frame_id] = frame

            if tags:
                for tag in tags:
                    if tag.startswith("character:"):
                        char_name = tag.split(":")[1]
                        if char_name not in self.character_library:
                            self.character_library[char_name] = []
                        self.character_library[char_name].append(frame.frame_id)

                    elif tag.startswith("object:"):
                        obj_name = tag.split(":")[1]
                        if obj_name not in self.object_library:
                            self.object_library[obj_name] = []
                        self.object_library[obj_name].append(frame.frame_id)

            return True
        except Exception as e:
            self.logger.error(f"Error adding reference: {e}")
            return False

    def get_reference(self, frame_id: str) -> Optional[ReferenceFrame]:
        """Retrieve a reference frame"""
        return self.references.get(frame_id)

    def get_character_references(self, character_name: str) -> List[ReferenceFrame]:
        """Get all references for a character"""
        frame_ids = self.character_library.get(character_name, [])
        return [self.references[fid] for fid in frame_ids if fid in self.references]

    def get_similar_references(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar references using embedding similarity"""
        similarities = []

        for frame_id, frame in self.references.items():
            if "visual" not in frame.embeddings:
                continue

            similarity = self._cosine_similarity(query_embedding, frame.embeddings["visual"])
            similarities.append((frame_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


class StyleExtractor:
    """
    Extract style features from scene analysis
    Integrates with scene_analyzer.py
    """

    def __init__(self, scene_analyzer=None):
        self.scene_analyzer = scene_analyzer
        self.logger = logging.getLogger(__name__)

    def extract_style_from_image(self, image_path: str) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Extract style features directly from image
        Returns style features dict and embedding
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            color_palette = self._extract_dominant_colors(image)
            lighting_style = self._analyze_lighting(image, gray)
            texture_profile = self._analyze_texture(gray)
            composition_style = self._analyze_composition(gray)

            style_features = {
                "color_palette": color_palette,
                "lighting_style": lighting_style,
                "texture_profile": texture_profile,
                "composition_style": composition_style,
            }

            embedding = self.create_style_embedding(style_features)

            return style_features, embedding

        except Exception as e:
            self.logger.error(f"Error extracting style from image: {e}")
            return {}, np.zeros(64, dtype=np.float32)

    def _extract_dominant_colors(self, image: np.ndarray, n_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using k-means"""
        pixels = image.reshape(-1, 3)
        pixels = np.float32(pixels)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        centers = np.uint8(centers)
        colors = [tuple(map(int, color)) for color in centers]

        return colors

    def _analyze_lighting(self, image: np.ndarray, gray: np.ndarray) -> Dict[str, Any]:
        """Analyze lighting characteristics"""
        brightness = np.mean(gray)
        contrast = np.std(gray)

        intensity = "high" if brightness > 180 else "low" if brightness < 80 else "medium"

        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist / hist.sum()

        low_key = np.sum(hist_norm[:85])
        high_key = np.sum(hist_norm[170:])

        quality = "high_key" if high_key > 0.4 else "low_key" if low_key > 0.4 else "balanced"

        return {
            "intensity": intensity,
            "brightness": float(brightness),
            "contrast": float(contrast),
            "quality": quality,
            "color_temperature": 5500,
        }

    def _analyze_texture(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze texture characteristics"""
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_variance = laplacian.var()

        kernel = np.ones((5, 5), np.float32) / 25
        local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        local_var = cv2.filter2D((gray.astype(np.float32) ** 2), -1, kernel) - local_mean**2

        complexity = float(np.mean(np.sqrt(np.abs(local_var))))
        smoothness = 1.0 - min(texture_variance / 1000.0, 1.0)

        return {"complexity": complexity / 255.0, "smoothness": smoothness, "detail_level": float(texture_variance) / 1000.0}

    def _analyze_composition(self, gray: np.ndarray) -> Dict[str, Any]:
        """Analyze composition style"""
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])

        return {
            "edge_density": float(edge_density),
            "complexity": "high" if edge_density > 0.1 else "medium" if edge_density > 0.05 else "low",
        }

    def extract_style_from_analysis(self, scene_analysis: Dict) -> Dict[str, Any]:
        """Extract style features from scene analysis"""
        style_features = {
            "color_palette": self._extract_color_palette(scene_analysis),
            "composition_style": self._extract_composition_style(scene_analysis),
            "lighting_style": self._extract_lighting_style(scene_analysis),
            "texture_profile": self._extract_texture_profile(scene_analysis),
            "scene_atmosphere": self._extract_atmosphere(scene_analysis),
        }
        return style_features

    def _extract_color_palette(self, analysis: Dict) -> List[Tuple[int, int, int]]:
        """Extract dominant color palette"""
        palette = []

        if "scene_type" in analysis and "color_ratios" in analysis["scene_type"]:
            ratios = analysis["scene_type"]["color_ratios"]

            color_map = {
                "sky": (135, 206, 235),
                "vegetation": (34, 139, 34),
                "building": (169, 169, 169),
                "water": (65, 105, 225),
            }

            for scene_type, ratio in ratios.items():
                if ratio > 0.1 and scene_type in color_map:
                    palette.append(color_map[scene_type])

        return palette[:5]

    def _extract_composition_style(self, analysis: Dict) -> Dict[str, Any]:
        """Extract composition style characteristics"""
        comp_style = {"rule_of_thirds_adherence": 0.0, "symmetry_type": "none", "balance": "neutral"}

        if "composition" in analysis:
            comp = analysis["composition"]

            if "symmetry" in comp:
                h_sym = comp["symmetry"].get("horizontal_symmetry", 0)
                v_sym = comp["symmetry"].get("vertical_symmetry", 0)

                if h_sym > 0.7:
                    comp_style["symmetry_type"] = "horizontal"
                elif v_sym > 0.7:
                    comp_style["symmetry_type"] = "vertical"
                elif h_sym > 0.5 and v_sym > 0.5:
                    comp_style["symmetry_type"] = "radial"

            if "complexity" in comp:
                edge_density = comp["complexity"].get("edge_density", 0)
                comp_style["complexity"] = "high" if edge_density > 0.3 else "low"

        return comp_style

    def _extract_lighting_style(self, analysis: Dict) -> Dict[str, Any]:
        """Extract lighting style characteristics"""
        lighting = {"intensity": "medium", "direction": "frontal", "quality": "soft"}

        if "image_info" in analysis:
            brightness = analysis["image_info"].get("mean_brightness", 128)

            if brightness > 180:
                lighting["intensity"] = "high"
            elif brightness < 80:
                lighting["intensity"] = "low"

        return lighting

    def _extract_texture_profile(self, analysis: Dict) -> Dict[str, float]:
        """Extract texture characteristics"""
        texture = {"complexity": 0.5, "smoothness": 0.5, "detail_level": 0.5}

        if "composition" in analysis and "complexity" in analysis["composition"]:
            texture["complexity"] = analysis["composition"]["complexity"].get("texture_complexity", 0.5)
            texture["detail_level"] = analysis["composition"]["complexity"].get("edge_density", 0.5)

        return texture

    def _extract_atmosphere(self, analysis: Dict) -> str:
        """Determine overall scene atmosphere"""
        if "scene_type" in analysis:
            scene_type = analysis["scene_type"].get("type", "mixed")

            atmosphere_map = {
                "landscape": "serene",
                "urban": "dynamic",
                "water_scene": "calm",
                "nature": "organic",
                "sky": "ethereal",
                "mixed": "balanced",
            }

            return atmosphere_map.get(scene_type, "neutral")

        return "neutral"

    def create_style_embedding(self, style_features: Dict) -> np.ndarray:
        """Create numerical embedding from style features"""
        embedding_components = []

        if "color_palette" in style_features:
            palette = style_features["color_palette"]
            for color in palette[:5]:
                embedding_components.extend([c / 255.0 for c in color])

        while len(embedding_components) < 15:
            embedding_components.append(0.0)

        comp_style = style_features.get("composition_style", {})
        embedding_components.append(comp_style.get("rule_of_thirds_adherence", 0.5))

        lighting = style_features.get("lighting_style", {})
        intensity_map = {"low": 0.25, "medium": 0.5, "high": 0.75}
        embedding_components.append(intensity_map.get(lighting.get("intensity", "medium"), 0.5))

        texture = style_features.get("texture_profile", {})
        embedding_components.append(texture.get("complexity", 0.5))
        embedding_components.append(texture.get("smoothness", 0.5))

        while len(embedding_components) < 64:
            embedding_components.append(0.0)

        return np.array(embedding_components[:64], dtype=np.float32)


class CrossShotValidator:
    """
    Validates consistency across multiple shots
    """

    def __init__(self, reference_library: ReferenceLibrary, rules: Optional[List[ContinuityRule]] = None):
        self.reference_library = reference_library
        self.rules = rules or self._create_default_rules()
        self.logger = logging.getLogger(__name__)

    def _create_default_rules(self) -> List[ContinuityRule]:
        """Create default continuity rules"""
        return [
            ColorConsistencyRule(threshold=0.1),
            LightingContinuityRule(threshold=0.15),
            SpatialCoherenceRule(threshold=0.2),
        ]

    def validate_shot_sequence(self, shots: List[ReferenceFrame], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate consistency across a sequence of shots"""
        violations = []
        rule_scores = {rule.rule_id: [] for rule in self.rules}

        for i in range(len(shots) - 1):
            frame_a = shots[i]
            frame_b = shots[i + 1]

            for rule in self.rules:
                if not rule.enabled:
                    continue

                score = rule.evaluate(frame_a, frame_b)

                if score is not None:
                    rule_scores[rule.rule_id].append(score)

                    if score < rule.threshold:
                        violation = ConsistencyViolation(
                            violation_type=rule.rule_type,
                            severity=(rule.threshold - score) * rule.weight,
                            description=f"{rule.name} violation: score {score:.2f} below threshold {rule.threshold}",
                            frame_a=frame_a.frame_id,
                            frame_b=frame_b.frame_id,
                            suggested_fix=self._generate_fix_suggestion(rule, score, frame_a, frame_b),
                            confidence=0.85,
                            details={"score": score, "threshold": rule.threshold},
                        )
                        violations.append(violation)

        aggregate_scores = {}
        for rule_id, scores in rule_scores.items():
            if scores:
                aggregate_scores[rule_id] = {
                    "mean": float(np.mean(scores)),
                    "min": float(np.min(scores)),
                    "max": float(np.max(scores)),
                    "std": float(np.std(scores)),
                }

        return {
            "violations": violations,
            "rule_scores": aggregate_scores,
            "overall_consistency": self._calculate_overall_consistency(aggregate_scores),
            "total_checks": len(shots) - 1,
            "passed": len(violations) == 0,
        }

    def _generate_fix_suggestion(
        self, rule: ContinuityRule, score: float, frame_a: ReferenceFrame, frame_b: ReferenceFrame
    ) -> str:
        """Generate specific fix suggestion for violation"""
        suggestions = {
            "color_consistency": "Apply color grading to match reference frame's color palette",
            "lighting_continuity": "Adjust lighting intensity and color temperature to match",
            "spatial_coherence": "Verify and correct object positions to maintain spatial relationships",
        }
        return suggestions.get(rule.rule_id, "Review and adjust to match reference frame")

    def _calculate_overall_consistency(self, aggregate_scores: Dict) -> float:
        """Calculate overall consistency score"""
        if not aggregate_scores:
            return 1.0

        mean_scores = [scores["mean"] for scores in aggregate_scores.values()]
        return float(np.mean(mean_scores)) if mean_scores else 1.0

    def validate_character_consistency(self, character_id: str, shots: List[ReferenceFrame]) -> Dict[str, Any]:
        """Validate specific character consistency across shots"""
        character_ref = self.reference_library.get_character(character_id)
        if not character_ref:
            return {"error": f"Character {character_id} not found in library"}

        violations = []
        appearance_scores = []

        for shot in shots:
            if character_id in shot.character_ids:
                if "character" in shot.embeddings:
                    similarity = self._cosine_similarity(
                        character_ref.appearance_embedding, shot.embeddings["character"]
                    )
                    appearance_scores.append(similarity)

                    if similarity < 0.85:
                        violations.append(
                            {"frame_id": shot.frame_id, "similarity": similarity, "severity": 1.0 - similarity}
                        )

        return {
            "character_id": character_id,
            "character_name": character_ref.name,
            "appearances": len(appearance_scores),
            "mean_similarity": float(np.mean(appearance_scores)) if appearance_scores else 0.0,
            "min_similarity": float(np.min(appearance_scores)) if appearance_scores else 0.0,
            "violations": violations,
            "consistency_rating": "high" if len(violations) == 0 else "needs_review",
        }

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


class ConsistencyEngine:
    """
    Consistency Engine - Strategic Wedge Feature

    Creates defensible moat through:
    - Multi-model ensemble for identity preservation
    - Proprietary consistency corpus
    - Real-time validation with immediate feedback
    - Learning system that improves from corrections

    Measurement Metrics:
    - Cross-shot consistency: >85% match
    - Character identity: >95% F1 score
    - Lighting coherence: <10% ΔRGB variance
    - Spatial accuracy: <5% position deviation
    """

    def __init__(
        self,
        reference_manager: Optional[ReferenceManager] = None,
        reference_library: Optional[ReferenceLibrary] = None,
        config_path: Optional[str] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.reference_manager = reference_manager or ReferenceManager()
        self.reference_library = reference_library or ReferenceLibrary()
        self.config_path = config_path or "configs/consistency_engine.json"
        self.consistency_history: List[ConsistencyViolation] = []
        self.thresholds = {
            "character_identity": 0.95,
            "lighting": 0.85,
            "color_grading": 0.90,
            "spatial_relationship": 0.88,
            "object_appearance": 0.92,
            "style": 0.88,
            "world": 0.85,
        }

        self.style_extractor = StyleExtractor()
        self.validator = CrossShotValidator(self.reference_library)

        self._load_config()

    def _load_config(self):
        """Load configuration"""
        config_path = Path(self.config_path)
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.thresholds.update(config.get("thresholds", {}))
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

    def integrate_scene_analysis(
        self, frame_id: str, scene_analysis: Dict, shot_id: str, timestamp: float = 0.0
    ) -> ReferenceFrame:
        """
        Integrate scene analysis from scene_analyzer.py
        Creates reference frame with extracted features
        """
        style_features = self.style_extractor.extract_style_from_analysis(scene_analysis)
        style_embedding = self.style_extractor.create_style_embedding(style_features)
        color_histogram = self._extract_color_histogram_from_analysis(scene_analysis)
        lighting_profile = self._extract_lighting_from_analysis(scene_analysis)

        frame = ReferenceFrame(
            frame_id=frame_id,
            shot_id=shot_id,
            timestamp=timestamp,
            embeddings={"style": style_embedding},
            metadata={"scene_analysis": scene_analysis, "style_features": style_features},
            color_histogram=color_histogram,
            lighting_profile=lighting_profile,
        )

        return frame

    def create_reference_from_image(
        self, frame_id: str, image_path: str, shot_id: str, timestamp: float = 0.0
    ) -> ReferenceFrame:
        """
        Create reference frame directly from image
        """
        style_features, style_embedding = self.style_extractor.extract_style_from_image(image_path)

        image = cv2.imread(image_path)
        color_histogram = self._extract_color_histogram_from_image(image)
        lighting_profile = style_features.get("lighting_style", {})

        frame = ReferenceFrame(
            frame_id=frame_id,
            shot_id=shot_id,
            timestamp=timestamp,
            embeddings={"style": style_embedding},
            metadata={"image_path": image_path, "style_features": style_features},
            color_histogram=color_histogram,
            lighting_profile=lighting_profile,
        )

        return frame

    def _extract_color_histogram_from_image(self, image: np.ndarray) -> np.ndarray:
        """Extract color histogram from image"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])

        hist_h = hist_h / hist_h.sum()
        hist_s = hist_s / hist_s.sum()
        hist_v = hist_v / hist_v.sum()

        histogram = np.concatenate([hist_h.flatten()[:30], hist_s.flatten()[:30], hist_v.flatten()[:30]])
        return histogram

    def _extract_color_histogram_from_analysis(self, analysis: Dict) -> Optional[np.ndarray]:
        """Extract color histogram from scene analysis"""
        if "scene_type" in analysis and "color_ratios" in analysis["scene_type"]:
            ratios = analysis["scene_type"]["color_ratios"]
            histogram = np.array(
                [ratios.get("sky", 0), ratios.get("vegetation", 0), ratios.get("building", 0), ratios.get("water", 0)]
            )
            return histogram
        return None

    def _extract_lighting_from_analysis(self, analysis: Dict) -> Optional[Dict]:
        """Extract lighting profile from scene analysis"""
        if "image_info" in analysis:
            brightness = analysis["image_info"].get("mean_brightness", 128)

            return {
                "intensity": brightness / 255.0,
                "color_temperature": 5500,
                "direction": "frontal",
                "quality": "soft",
            }
        return None

    def check_character_consistency(
        self, frame_a: ReferenceFrame, frame_b: ReferenceFrame, character_name: str
    ) -> Optional[ConsistencyViolation]:
        """Check character appearance consistency between frames"""
        if "character" not in frame_a.embeddings or "character" not in frame_b.embeddings:
            return None

        similarity = self.reference_manager._cosine_similarity(
            frame_a.embeddings["character"], frame_b.embeddings["character"]
        )

        threshold = self.thresholds["character_identity"]

        if similarity < threshold:
            return ConsistencyViolation(
                violation_type=ConsistencyType.CHARACTER_IDENTITY,
                severity=1.0 - similarity,
                description=f"Character '{character_name}' appearance mismatch",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Re-generate with reference frame or adjust prompt",
                confidence=0.9,
                details={"similarity": similarity, "threshold": threshold},
            )

        return None

    def check_lighting_consistency(
        self, frame_a: ReferenceFrame, frame_b: ReferenceFrame
    ) -> Optional[ConsistencyViolation]:
        """Check lighting consistency between frames"""
        if not frame_a.lighting_profile or not frame_b.lighting_profile:
            return None

        intensity_diff = abs(
            frame_a.lighting_profile.get("intensity", 0) - frame_b.lighting_profile.get("intensity", 0)
        )

        color_temp_diff = abs(
            frame_a.lighting_profile.get("color_temperature", 5500)
            - frame_b.lighting_profile.get("color_temperature", 5500)
        )

        if intensity_diff > 0.2 or color_temp_diff > 1000:
            return ConsistencyViolation(
                violation_type=ConsistencyType.LIGHTING,
                severity=max(intensity_diff, color_temp_diff / 5000),
                description=f"Lighting mismatch: intensity Δ{intensity_diff:.2f}, temp Δ{color_temp_diff}K",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Adjust lighting to match reference",
                confidence=0.85,
                details={"intensity_diff": intensity_diff, "color_temp_diff": color_temp_diff},
            )

        return None

    def check_color_consistency(
        self, frame_a: ReferenceFrame, frame_b: ReferenceFrame
    ) -> Optional[ConsistencyViolation]:
        """Check color grading consistency"""
        if frame_a.color_histogram is None or frame_b.color_histogram is None:
            return None

        hist_diff = np.sum(np.abs(frame_a.color_histogram - frame_b.color_histogram))

        threshold = self.thresholds["color_grading"]

        if hist_diff > (1.0 - threshold):
            return ConsistencyViolation(
                violation_type=ConsistencyType.COLOR_GRADING,
                severity=float(hist_diff),
                description=f"Color grading mismatch: histogram diff {hist_diff:.3f}",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Apply color matching LUT or grade adjustment",
                confidence=0.88,
                details={"histogram_diff": hist_diff},
            )

        return None

    def check_spatial_consistency(
        self, frame_a: ReferenceFrame, frame_b: ReferenceFrame, object_id: str
    ) -> Optional[ConsistencyViolation]:
        """Check spatial relationship consistency"""
        if object_id not in frame_a.character_positions or object_id not in frame_b.character_positions:
            return None

        pos_a = frame_a.character_positions[object_id]
        pos_b = frame_b.character_positions[object_id]

        distance = np.sqrt((pos_a[0] - pos_b[0]) ** 2 + (pos_a[1] - pos_b[1]) ** 2)

        threshold = 0.12

        if distance > threshold:
            return ConsistencyViolation(
                violation_type=ConsistencyType.SPATIAL_RELATIONSHIP,
                severity=float(distance),
                description=f"Spatial position mismatch for {object_id}: {distance:.3f}",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Adjust framing or object position",
                confidence=0.80,
                details={"distance": distance, "threshold": threshold},
            )

        return None

    def validate_shot_sequence(
        self, frames: List[ReferenceFrame], check_types: Optional[List[ConsistencyType]] = None
    ) -> List[ConsistencyViolation]:
        """Validate consistency across a sequence of frames"""
        violations = []

        check_types = check_types or [
            ConsistencyType.CHARACTER_IDENTITY,
            ConsistencyType.LIGHTING,
            ConsistencyType.COLOR_GRADING,
        ]

        for i in range(len(frames) - 1):
            frame_a = frames[i]
            frame_b = frames[i + 1]

            if ConsistencyType.CHARACTER_IDENTITY in check_types:
                for char_name in frame_a.character_positions.keys():
                    violation = self.check_character_consistency(frame_a, frame_b, char_name)
                    if violation:
                        violations.append(violation)

            if ConsistencyType.LIGHTING in check_types:
                violation = self.check_lighting_consistency(frame_a, frame_b)
                if violation:
                    violations.append(violation)

            if ConsistencyType.COLOR_GRADING in check_types:
                violation = self.check_color_consistency(frame_a, frame_b)
                if violation:
                    violations.append(violation)

        self.consistency_history.extend(violations)
        return violations

    def get_consistency_score(self, frames: List[ReferenceFrame]) -> Dict[str, float]:
        """Calculate overall consistency scores"""
        violations = self.validate_shot_sequence(frames)

        total_checks = len(frames) - 1
        if total_checks == 0:
            return {"overall": 1.0}

        violation_counts = {}
        for v in violations:
            v_type = v.violation_type.value
            violation_counts[v_type] = violation_counts.get(v_type, 0) + 1

        scores = {
            "overall": 1.0 - (len(violations) / (total_checks * 3)),
            "character_identity": 1.0 - (violation_counts.get("character_identity", 0) / total_checks),
            "lighting": 1.0 - (violation_counts.get("lighting", 0) / total_checks),
            "color_grading": 1.0 - (violation_counts.get("color_grading", 0) / total_checks),
            "total_violations": len(violations),
            "avg_severity": float(np.mean([v.severity for v in violations])) if violations else 0.0,
        }

        return scores

    def generate_consistency_report(self, frames: List[ReferenceFrame]) -> Dict:
        """Generate detailed consistency report"""
        violations = self.validate_shot_sequence(frames)
        scores = self.get_consistency_score(frames)

        return {
            "summary": {
                "total_frames": len(frames),
                "total_violations": len(violations),
                "consistency_score": scores["overall"],
                "pass_threshold": scores["overall"] >= 0.85,
            },
            "scores_by_type": {
                "character_identity": scores.get("character_identity", 1.0),
                "lighting": scores.get("lighting", 1.0),
                "color_grading": scores.get("color_grading", 1.0),
            },
            "violations": [
                {
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "description": v.description,
                    "frames": [v.frame_a, v.frame_b],
                    "suggested_fix": v.suggested_fix,
                    "confidence": v.confidence,
                    "details": v.details,
                }
                for v in violations
            ],
            "recommendations": self._generate_recommendations(violations),
        }

    def _generate_recommendations(self, violations: List[ConsistencyViolation]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        character_violations = [v for v in violations if v.violation_type == ConsistencyType.CHARACTER_IDENTITY]
        if len(character_violations) > 2:
            recommendations.append(
                "HIGH PRIORITY: Multiple character identity violations detected. "
                "Consider using reference images or fine-tuning character embeddings."
            )

        lighting_violations = [v for v in violations if v.violation_type == ConsistencyType.LIGHTING]
        if len(lighting_violations) > 1:
            recommendations.append(
                "Lighting inconsistency detected. Apply consistent lighting keywords "
                "or use color grading to match reference frames."
            )

        severe_violations = [v for v in violations if v.severity > 0.5]
        if severe_violations:
            recommendations.append(
                f"{len(severe_violations)} severe violations require immediate attention. "
                "Review suggested fixes in detail."
            )

        return recommendations
