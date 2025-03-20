from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#db.init_app(app)
from datetime import datetime, timedelta

def convert_to_beijing_time(utc_time):
    """将 UTC 时间转换为北京时间（UTC+8）"""
    return utc_time + timedelta(hours=8)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))

    # 添加关系方便查询
    model_services = db.relationship('ModelService', backref='project', cascade="all, delete-orphan")


class Feature(db.Model):
    __tablename__ = 'features'
    id = db.Column(db.Integer, primary_key=True)
    model_service_id = db.Column(db.Integer, db.ForeignKey('model_services.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='candidate')
    parameters = db.Column(db.JSON)
    version = db.Column(db.Integer, default=1)
    chinese_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8), onupdate=lambda: datetime.utcnow() + timedelta(hours=8))


class FeatureVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('features.id'), nullable=False)
    version = db.Column(db.Integer)
    status = db.Column(db.String(20))
    parameters = db.Column(db.JSON)
    chinese_name = db.Column(db.String(100))  # 新增字段
    description = db.Column(db.Text)  # 新增字段
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))

    # 关系定义
    feature = db.relationship('Feature', backref=db.backref('versions', lazy=True))

class ModelService(db.Model):
    __tablename__ = 'model_services'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    features = db.relationship('Feature', backref='model_service', cascade="all, delete-orphan")


class Version(db.Model):
    __tablename__ = 'versions'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8), onupdate=lambda: datetime.utcnow() + timedelta(hours=8))

@app.route('/')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    features = Feature.query.join(ModelService).filter(ModelService.project_id == project_id).all()
    return render_template('project_detail.html', project=project, features=features)

@app.route('/model_service/<int:model_service_id>')
def model_service_detail(model_service_id):
    model_service = ModelService.query.get_or_404(model_service_id)
    features = Feature.query.filter_by(model_service_id=model_service_id).all()
    return render_template('model_service_detail.html', model_service=model_service, features=features)


@app.route('/api/project', methods=['POST'])
def create_project():
    data = request.get_json()
    project = Project(
        name=data['name'],
        description=data['description']
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'id': project.id}), 201

@app.route('/api/feature', methods=['POST'])
def create_feature():
    data = request.get_json()
    feature = Feature(
        model_service_id=data['model_service_id'],
        name=data['name'],
        chinese_name=data['chinese_name'],
        description=data['description'],
        data_type=data['data_type'],
        parameters=data.get('parameters')
    )
    db.session.add(feature)
    db.session.commit()
    # 创建初始版本记录
    feature_version = FeatureVersion(
        feature_id=feature.id,
        version=feature.version,
        status=feature.status,
        parameters=feature.parameters,
        chinese_name=feature.chinese_name,
        description=feature.description,
        updated_at=feature.updated_at
    )
    db.session.add(feature_version)
    db.session.commit()
    return jsonify({'id': feature.id}), 201

@app.route('/api/features/export', methods=['POST'])
def export_features():
    feature_ids = request.json.get('feature_ids', [])
    features = Feature.query.filter(Feature.id.in_(feature_ids)).all()
    features_data = [{
        'name': f.name,
        'data_type': f.data_type,
        'parameters': f.parameters,
        'status': f.status
    } for f in features]
    return jsonify(features_data)


# app.py 新增API端点
@app.route('/api/project/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description
        })
        
    if request.method == 'PUT':
        data = request.get_json()
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.version += 1
        db.session.commit()
        return jsonify({'message': 'Project updated'}), 200
        
    if request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted'}), 200

# app.py 新增特征管理端点
@app.route('/api/feature/<int:feature_id>', methods=['GET', 'PATCH'])
def manage_feature(feature_id):
    feature = Feature.query.get_or_404(feature_id)

    if request.method == 'GET':
        return jsonify({
            'id': feature.id,
            'name': feature.name,
            'chinese_name': feature.chinese_name,
            'description': feature.description,
            'data_type': feature.data_type,
            'status': feature.status,
            'parameters': feature.parameters,
            'version': feature.version,
            'created_at': convert_to_beijing_time(feature.created_at).strftime('%m-%d %H:%M'),  # 转换为北京时间
            'updated_at': convert_to_beijing_time(feature.updated_at).strftime('%m-%d %H:%M')  # 转换为北京时间
        })

    elif request.method == 'PATCH':
        data = request.get_json()
        feature.name = data.get('name', feature.name)
        feature.chinese_name = data.get('chinese_name', feature.chinese_name)
        feature.description = data.get('description', feature.description)
        feature.data_type = data.get('data_type', feature.data_type)
        feature.parameters = data.get('parameters', feature.parameters)
        feature.version += 1
        feature.updated_at = datetime.utcnow() + timedelta(hours=8)
        # 创建新的历史记录
        feature_version = FeatureVersion(
            feature_id=feature.id,
            version=feature.version,
            status=feature.status,
            parameters=feature.parameters,
            chinese_name=feature.chinese_name,  # 填充中文名
            description=feature.description,  # 填充描述
            updated_at=feature.updated_at
        )
        db.session.add(feature_version)

        db.session.commit()
        return jsonify({'message': 'Feature updated'}), 200


# 在app.py中添加
@app.route('/api/feature/<int:feature_id>/history')
def get_feature_history(feature_id):
    current = Feature.query.get_or_404(feature_id)
    versions = FeatureVersion.query.filter_by(feature_id=feature_id).order_by(FeatureVersion.version.desc()).all()
    
    return jsonify({
        'current': {
            'id': current.id,
            'name': current.name,
            'version': current.version
        },
        'versions': [{
            'version': v.version,
            'status': v.status,
            'parameters': v.parameters,
            'description': v.description,
            'chinese_name': v.chinese_name,
            'updated_at': v.updated_at.isoformat()
        } for v in versions]
    })

@app.route('/api/project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# app.py 新增特征管理端点
@app.route('/api/feature2/<int:feature_id>', methods=['PATCH', 'DELETE'])
def manage_feature2(feature_id):
    feature = Feature.query.get_or_404(feature_id)
    if request.method == 'PATCH':
        data = request.get_json()
        print(data,"data")
        if 'status' in data:
            feature.status = data['status']
        feature.version += 1
        feature.updated_at = datetime.utcnow() + timedelta(hours=8)
        db.session.commit()
        return jsonify({'message': 'Feature updated'}), 200
    elif request.method == 'DELETE':
        print(request,"request")
        # Manually delete related FeatureVersion records
        FeatureVersion.query.filter_by(feature_id=feature.id).delete()
        db.session.delete(feature)
        db.session.commit()
        return jsonify({'message': 'Feature deleted'}), 200

@app.route('/api/model_service', methods=['POST'])
def create_model_service():
    data = request.get_json()
    model_service = ModelService(
        project_id=data['project_id'],
        name=data['name'],
        description=data['description']
    )
    db.session.add(model_service)
    db.session.commit()
    return jsonify({'id': model_service.id}), 201


@app.route('/api/version', methods=['POST'])
def create_version():
    data = request.get_json()
    version = Version(
        project_id=data['project_id'],
        name=data['name'],
        description=data['description'],
        feedback=data.get('feedback')
    )
    db.session.add(version)
    db.session.commit()
    return jsonify({'id': version.id}), 201

@app.route('/api/version/<int:version_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_version(version_id):
    version = Version.query.get_or_404(version_id)
    if request.method == 'GET':
        return jsonify({
            'id': version.id,
            'name': version.name,
            'description': version.description,
            'feedback': version.feedback
        })
    elif request.method == 'PUT':
        data = request.get_json()
        version.name = data.get('name', version.name)
        version.description = data.get('description', version.description)
        version.feedback = data.get('feedback', version.feedback)
        version.updated_at = datetime.utcnow() + timedelta(hours=8)
        db.session.commit()
        return jsonify({'message': 'Version updated'}), 200
    elif request.method == 'DELETE':
        db.session.delete(version)
        db.session.commit()
        return jsonify({'message': 'Version deleted'}), 200

@app.route('/api/project/<int:project_id>/versions', methods=['GET'])
def get_project_versions(project_id):
    versions = Version.query.filter_by(project_id=project_id).all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'description': v.description,
        'feedback': v.feedback,
        'created_at': convert_to_beijing_time(v.created_at).strftime('%Y-%m-%d %H:%M'),
        'updated_at': convert_to_beijing_time(v.updated_at).strftime('%Y-%m-%d %H:%M')
    } for v in versions])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5007)