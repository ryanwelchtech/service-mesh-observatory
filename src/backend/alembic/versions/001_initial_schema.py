"""Initial schema - create all tables

Revision ID: 001
Revises:
Create Date: 2024-12-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'OPERATOR', 'VIEWER', name='userrole'), nullable=False, default='VIEWER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('api_key_hash', sa.String(255), nullable=True),
        sa.Column('last_login', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Anomalies table
    op.create_table(
        'anomalies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('anomaly_type', sa.Enum(
            'DATA_EXFILTRATION', 'LATERAL_MOVEMENT', 'REQUEST_SPIKE', 'ERROR_SPIKE',
            'LATENCY_SPIKE', 'UNAUTHORIZED_ACCESS', 'PORT_SCAN', 'CERTIFICATE_ISSUE',
            'POLICY_VIOLATION', 'UNKNOWN', name='anomalytype'
        ), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('pod_name', sa.String(255), nullable=True),
        sa.Column('source_ip', sa.String(45), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('detection_method', sa.String(100), nullable=True),
        sa.Column('contributing_factors', sa.JSON(), nullable=True),
        sa.Column('metrics_snapshot', sa.JSON(), nullable=True),
        sa.Column('is_acknowledged', sa.Boolean(), default=False, nullable=False),
        sa.Column('acknowledged_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('acknowledged_at', sa.String(50), nullable=True),
        sa.Column('acknowledgement_notes', sa.Text(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), default=False, nullable=False),
        sa.Column('resolved_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('resolved_at', sa.String(50), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('is_false_positive', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_anomalies_type', 'anomalies', ['anomaly_type'])
    op.create_index('ix_anomalies_severity', 'anomalies', ['severity'])
    op.create_index('ix_anomalies_service', 'anomalies', ['service_name', 'namespace'])

    # Service Metrics table (TimescaleDB hypertable candidate)
    op.create_table(
        'service_metrics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('request_rate', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('latency_p50', sa.Float(), nullable=True),
        sa.Column('latency_p95', sa.Float(), nullable=True),
        sa.Column('latency_p99', sa.Float(), nullable=True),
        sa.Column('latency_avg', sa.Float(), nullable=True),
        sa.Column('active_connections', sa.Integer(), nullable=True),
        sa.Column('connection_errors', sa.Integer(), nullable=True),
        sa.Column('mtls_requests', sa.Integer(), nullable=True),
        sa.Column('plaintext_requests', sa.Integer(), nullable=True),
        sa.Column('cpu_usage', sa.Float(), nullable=True),
        sa.Column('memory_usage', sa.Float(), nullable=True),
        sa.Column('response_codes', sa.JSON(), nullable=True),
    )
    op.create_index('ix_service_metrics_time_service', 'service_metrics', ['timestamp', 'service_name', 'namespace'])

    # Metric Snapshots table
    op.create_table(
        'metric_snapshots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('total_services', sa.Integer(), nullable=True),
        sa.Column('healthy_services', sa.Integer(), nullable=True),
        sa.Column('total_pods', sa.Integer(), nullable=True),
        sa.Column('mesh_request_rate', sa.Float(), nullable=True),
        sa.Column('mesh_error_rate', sa.Float(), nullable=True),
        sa.Column('mesh_latency_p95', sa.Float(), nullable=True),
        sa.Column('mtls_coverage', sa.Float(), nullable=True),
        sa.Column('policy_compliance', sa.Float(), nullable=True),
        sa.Column('certs_expiring_7d', sa.Integer(), nullable=True),
        sa.Column('certs_expiring_30d', sa.Integer(), nullable=True),
        sa.Column('total_certificates', sa.Integer(), nullable=True),
        sa.Column('active_anomalies', sa.Integer(), nullable=True),
        sa.Column('critical_anomalies', sa.Integer(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
    )
    op.create_index('ix_metric_snapshots_timestamp', 'metric_snapshots', ['timestamp'])

    # Certificates table
    op.create_table(
        'certificates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('pod_name', sa.String(255), nullable=True),
        sa.Column('serial_number', sa.String(255), nullable=True),
        sa.Column('issuer', sa.String(500), nullable=True),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('san', sa.Text(), nullable=True),
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('days_until_expiry', sa.String(10), nullable=True),
        sa.Column('status', sa.Enum('VALID', 'EXPIRING_SOON', 'EXPIRED', 'REVOKED', 'UNKNOWN', name='certstatus'), nullable=False, default='VALID'),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('chain_valid', sa.Boolean(), default=True, nullable=False),
        sa.Column('chain_length', sa.String(5), nullable=True),
        sa.Column('sha256_fingerprint', sa.String(64), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_certificates_service', 'certificates', ['service_name', 'namespace'])
    op.create_index('ix_certificates_expires', 'certificates', ['expires_at'])
    op.create_index('ix_certificates_status', 'certificates', ['status'])

    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('user_role', sa.String(50), nullable=True),
        sa.Column('action', sa.Enum(
            'LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_CHANGE', 'TOKEN_REFRESH',
            'USER_CREATE', 'USER_UPDATE', 'USER_DELETE', 'ROLE_CHANGE',
            'POLICY_VIEW', 'POLICY_TEST', 'POLICY_VALIDATE',
            'ANOMALY_ACKNOWLEDGE', 'ANOMALY_RESOLVE', 'ANOMALY_FALSE_POSITIVE',
            'CERT_RENEWAL_TRIGGER', 'CONFIG_CHANGE', 'EXPORT_DATA', 'API_ACCESS',
            name='auditaction'
        ), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('request_method', sa.String(10), nullable=True),
        sa.Column('request_path', sa.String(500), nullable=True),
        sa.Column('success', sa.String(5), default='true', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_id'])

    # Create TimescaleDB hypertable for service_metrics (if using TimescaleDB)
    # Uncomment if using TimescaleDB:
    # op.execute("SELECT create_hypertable('service_metrics', 'timestamp', migrate_data => true);")


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('certificates')
    op.drop_table('metric_snapshots')
    op.drop_table('service_metrics')
    op.drop_table('anomalies')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS auditaction')
    op.execute('DROP TYPE IF EXISTS certstatus')
    op.execute('DROP TYPE IF EXISTS severity')
    op.execute('DROP TYPE IF EXISTS anomalytype')
    op.execute('DROP TYPE IF EXISTS userrole')
