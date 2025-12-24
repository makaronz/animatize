"""
Collaborative Production Workflow - Wedge Feature #8

Team adoption creates network effects and lock-in through workflow integration.
"""

import json
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class UserRole(Enum):
    """User roles with different permissions"""
    ADMIN = "admin"
    DIRECTOR = "director"
    EDITOR = "editor"
    VIEWER = "viewer"
    CONTRIBUTOR = "contributor"


class AssetStatus(Enum):
    """Asset approval status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class User:
    """User profile"""
    user_id: str
    name: str
    email: str
    role: UserRole
    permissions: Set[str] = field(default_factory=set)


@dataclass
class Comment:
    """Comment on an asset"""
    comment_id: str
    user_id: str
    asset_id: str
    text: str
    timestamp: datetime
    frame_number: Optional[int] = None
    resolved: bool = False


@dataclass
class Version:
    """Version of an asset"""
    version_id: str
    asset_id: str
    version_number: int
    created_by: str
    created_at: datetime
    changes: List[str]
    file_path: str


@dataclass
class Project:
    """Collaborative project"""
    project_id: str
    name: str
    owner_id: str
    members: List[str]
    assets: List[str]
    created_at: datetime
    metadata: Dict = field(default_factory=dict)


class ProjectManager:
    """
    Manages collaborative projects
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or "data/projects"
        self.projects: Dict[str, Project] = {}
        
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
    
    def create_project(
        self,
        project_id: str,
        name: str,
        owner_id: str
    ) -> Project:
        """Create new collaborative project"""
        project = Project(
            project_id=project_id,
            name=name,
            owner_id=owner_id,
            members=[owner_id],
            assets=[],
            created_at=datetime.now()
        )
        
        self.projects[project_id] = project
        self._save_project(project)
        return project
    
    def add_member(
        self,
        project_id: str,
        user_id: str,
        invited_by: str
    ) -> bool:
        """Add member to project"""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        
        if user_id not in project.members:
            project.members.append(user_id)
            self._save_project(project)
            self.logger.info(f"User {user_id} added to project {project_id} by {invited_by}")
            return True
        
        return False
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def _save_project(self, project: Project):
        """Save project to disk"""
        project_path = Path(self.storage_path) / f"{project.project_id}.json"
        
        try:
            data = {
                'project_id': project.project_id,
                'name': project.name,
                'owner_id': project.owner_id,
                'members': project.members,
                'assets': project.assets,
                'created_at': project.created_at.isoformat(),
                'metadata': project.metadata
            }
            
            with open(project_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving project: {e}")


class CollaborativeWorkflow:
    """
    Collaborative Production Workflow - Strategic Wedge Feature
    
    Creates defensible moat through:
    - Multi-user project sharing with real-time sync
    - Role-based permissions for team organization
    - Version control for all prompts and outputs
    - Approval workflows for production gates
    
    Measurement Metrics:
    - Team adoption rate: >80% of invited users
    - Collaboration events: 50+ per project average
    - Version control usage: 90%+ of edits tracked
    - Approval workflow time: 60%+ reduction
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or "data/collaboration"
        self.users: Dict[str, User] = {}
        self.comments: Dict[str, List[Comment]] = {}
        self.versions: Dict[str, List[Version]] = {}
        self.project_manager = ProjectManager(storage_path)
        self.activity_log: List[Dict] = []
        
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
    
    def register_user(
        self,
        user_id: str,
        name: str,
        email: str,
        role: UserRole = UserRole.CONTRIBUTOR
    ) -> User:
        """Register new user"""
        permissions = self._get_default_permissions(role)
        
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            role=role,
            permissions=permissions
        )
        
        self.users[user_id] = user
        self._log_activity('user_registered', user_id, {'name': name, 'role': role.value})
        
        return user
    
    def _get_default_permissions(self, role: UserRole) -> Set[str]:
        """Get default permissions for role"""
        permissions = {
            UserRole.ADMIN: {'read', 'write', 'delete', 'manage_users', 'approve'},
            UserRole.DIRECTOR: {'read', 'write', 'approve', 'comment'},
            UserRole.EDITOR: {'read', 'write', 'comment'},
            UserRole.CONTRIBUTOR: {'read', 'write', 'comment'},
            UserRole.VIEWER: {'read', 'comment'}
        }
        
        return permissions.get(role, {'read'})
    
    def add_comment(
        self,
        comment_id: str,
        user_id: str,
        asset_id: str,
        text: str,
        frame_number: Optional[int] = None
    ) -> Comment:
        """Add comment to asset"""
        comment = Comment(
            comment_id=comment_id,
            user_id=user_id,
            asset_id=asset_id,
            text=text,
            timestamp=datetime.now(),
            frame_number=frame_number
        )
        
        if asset_id not in self.comments:
            self.comments[asset_id] = []
        
        self.comments[asset_id].append(comment)
        self._log_activity('comment_added', user_id, {
            'asset_id': asset_id,
            'frame_number': frame_number
        })
        
        return comment
    
    def create_version(
        self,
        version_id: str,
        asset_id: str,
        user_id: str,
        changes: List[str],
        file_path: str
    ) -> Version:
        """Create new version of asset"""
        if asset_id not in self.versions:
            self.versions[asset_id] = []
        
        version_number = len(self.versions[asset_id]) + 1
        
        version = Version(
            version_id=version_id,
            asset_id=asset_id,
            version_number=version_number,
            created_by=user_id,
            created_at=datetime.now(),
            changes=changes,
            file_path=file_path
        )
        
        self.versions[asset_id].append(version)
        self._log_activity('version_created', user_id, {
            'asset_id': asset_id,
            'version_number': version_number
        })
        
        return version
    
    def submit_for_approval(
        self,
        asset_id: str,
        user_id: str,
        approvers: List[str]
    ) -> bool:
        """Submit asset for approval"""
        if not self._check_permission(user_id, 'write'):
            return False
        
        self._log_activity('approval_requested', user_id, {
            'asset_id': asset_id,
            'approvers': approvers
        })
        
        return True
    
    def approve_asset(
        self,
        asset_id: str,
        approver_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> bool:
        """Approve or reject asset"""
        if not self._check_permission(approver_id, 'approve'):
            return False
        
        status = 'approved' if approved else 'rejected'
        
        self._log_activity('asset_reviewed', approver_id, {
            'asset_id': asset_id,
            'status': status,
            'feedback': feedback
        })
        
        return True
    
    def get_activity_timeline(
        self,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get activity timeline"""
        filtered = self.activity_log
        
        if project_id:
            filtered = [
                a for a in filtered
                if a.get('project_id') == project_id
            ]
        
        if user_id:
            filtered = [
                a for a in filtered
                if a.get('user_id') == user_id
            ]
        
        return filtered[-limit:]
    
    def get_collaboration_stats(self, project_id: str) -> Dict:
        """Get collaboration statistics for project"""
        project_activities = [
            a for a in self.activity_log
            if a.get('project_id') == project_id
        ]
        
        comment_count = sum(
            1 for a in project_activities
            if a.get('action') == 'comment_added'
        )
        
        version_count = sum(
            1 for a in project_activities
            if a.get('action') == 'version_created'
        )
        
        approval_count = sum(
            1 for a in project_activities
            if a.get('action') == 'asset_reviewed'
        )
        
        unique_contributors = len(set(
            a.get('user_id') for a in project_activities
            if a.get('user_id')
        ))
        
        return {
            'total_activities': len(project_activities),
            'comments': comment_count,
            'versions': version_count,
            'approvals': approval_count,
            'active_contributors': unique_contributors,
            'avg_activities_per_user': len(project_activities) / max(unique_contributors, 1)
        }
    
    def _check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        return permission in user.permissions
    
    def _log_activity(
        self,
        action: str,
        user_id: str,
        details: Dict,
        project_id: Optional[str] = None
    ):
        """Log activity"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'project_id': project_id,
            'details': details
        }
        
        self.activity_log.append(activity)
        
        if len(self.activity_log) > 10000:
            self._archive_old_activities()
    
    def _archive_old_activities(self):
        """Archive old activities to free memory"""
        archive_path = Path(self.storage_path) / "activity_archive.json"
        
        try:
            archived = self.activity_log[:-5000]
            
            with open(archive_path, 'a') as f:
                for activity in archived:
                    f.write(json.dumps(activity) + '\n')
            
            self.activity_log = self.activity_log[-5000:]
        except Exception as e:
            self.logger.error(f"Error archiving activities: {e}")
    
    def export_project_report(self, project_id: str, output_path: str) -> bool:
        """Export comprehensive project report"""
        try:
            project = self.project_manager.get_project(project_id)
            if not project:
                return False
            
            stats = self.get_collaboration_stats(project_id)
            timeline = self.get_activity_timeline(project_id=project_id)
            
            report = {
                'project': {
                    'id': project.project_id,
                    'name': project.name,
                    'owner': project.owner_id,
                    'members': project.members,
                    'created_at': project.created_at.isoformat()
                },
                'statistics': stats,
                'recent_activity': timeline[-50:],
                'team_members': [
                    {
                        'user_id': u.user_id,
                        'name': u.name,
                        'role': u.role.value
                    }
                    for u in self.users.values()
                    if u.user_id in project.members
                ]
            }
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error exporting project report: {e}")
            return False
