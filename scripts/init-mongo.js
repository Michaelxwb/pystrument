// MongoDB初始化脚本
// 在数据库启动时自动执行

// 切换到pystrument数据库
db = db.getSiblingDB('pystrument');

// 创建应用用户
db.createUser({
  user: 'pystrument_user',
  pwd: 'pystrument_password',
  roles: [
    {
      role: 'readWrite',
      db: 'pystrument'
    }
  ]
});

// 创建集合并设置初始索引
print('Creating collections and indexes...');

// 1. 项目集合
db.createCollection('projects');
db.projects.createIndex({ 'project_key': 1 }, { unique: true });
db.projects.createIndex({ 'name': 1 });
db.projects.createIndex({ 'status': 1 });
db.projects.createIndex({ 'created_at': 1 });
db.projects.createIndex({ 'last_activity': 1 });

// 2. 性能记录集合
db.createCollection('performance_records');
db.performance_records.createIndex({ 'trace_id': 1 }, { unique: true });
db.performance_records.createIndex({ 'project_key': 1 });
db.performance_records.createIndex({ 'project_key': 1, 'timestamp': -1 });
db.performance_records.createIndex({ 'request_info.path': 1 });
db.performance_records.createIndex({ 'request_info.method': 1 });
db.performance_records.createIndex({ 'response_info.status_code': 1 });
db.performance_records.createIndex({ 'performance_metrics.total_duration': 1 });
db.performance_records.createIndex({ 'timestamp': 1 }, { expireAfterSeconds: 7776000 }); // 90天自动删除

// 3. 函数调用详情集合
db.createCollection('function_calls');
db.function_calls.createIndex({ 'call_id': 1 }, { unique: true });
db.function_calls.createIndex({ 'trace_id': 1 });
db.function_calls.createIndex({ 'trace_id': 1, 'call_context.call_order': 1 });
db.function_calls.createIndex({ 'function_info.name': 1 });
db.function_calls.createIndex({ 'execution_info.duration': 1 });
db.function_calls.createIndex({ 'performance_tags': 1 });
db.function_calls.createIndex({ 'created_at': 1 }, { expireAfterSeconds: 7776000 }); // 90天自动删除

// 4. AI分析结果集合
db.createCollection('ai_analysis_results');
db.ai_analysis_results.createIndex({ 'analysis_id': 1 }, { unique: true });
db.ai_analysis_results.createIndex({ 'project_key': 1 });
db.ai_analysis_results.createIndex({ 'trace_id': 1 });
db.ai_analysis_results.createIndex({ 'status': 1 });
db.ai_analysis_results.createIndex({ 'project_key': 1, 'created_at': -1 });
db.ai_analysis_results.createIndex({ 'analysis_type': 1 });
db.ai_analysis_results.createIndex({ 'created_at': 1 }, { expireAfterSeconds: 15552000 }); // 180天自动删除

// 5. 系统配置集合
db.createCollection('system_config');
db.system_config.createIndex({ 'config_key': 1 }, { unique: true });
db.system_config.createIndex({ 'category': 1 });
db.system_config.createIndex({ 'is_active': 1 });

print('Collections and indexes created successfully!');

// 插入默认系统配置
print('Inserting default system configurations...');

// 默认AI服务配置
db.system_config.insertOne({
  config_key: 'ai_service_default',
  config_value: {
    provider: 'openai',
    model: 'gpt-4',
    temperature: 0.3,
    max_tokens: 4000,
    enabled: true
  },
  description: '默认AI服务配置',
  category: 'ai',
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
});

// 默认监控配置
db.system_config.insertOne({
  config_key: 'monitoring_default',
  config_value: {
    sampling_rate: 0.3,
    slow_threshold: 1.0,
    batch_size: 50,
    batch_timeout: 5.0,
    enabled: true
  },
  description: '默认监控配置',
  category: 'monitoring',
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
});

// 默认告警配置
db.system_config.insertOne({
  config_key: 'alert_rules_default',
  config_value: {
    response_time_threshold: 2.0,
    error_rate_threshold: 0.05,
    memory_threshold: 512,
    enabled: true,
    notification_channels: ['email', 'webhook']
  },
  description: '默认告警规则配置',
  category: 'alert',
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
});

// 插入示例项目（用于演示）
print('Inserting demo project...');

db.projects.insertOne({
  project_key: 'demo_project_001',
  name: '演示项目',
  description: '用于演示性能分析平台功能的示例项目',
  framework: 'flask',
  status: 'active',
  config: {
    sampling_rate: 0.5,
    enabled: true,
    auto_analysis: true,
    alert_threshold: {
      response_time: 2.0,
      error_rate: 0.05,
      memory_usage: 512
    }
  },
  created_at: new Date(),
  updated_at: new Date(),
  last_activity: null
});

print('Demo project created with key: demo_project_001');

print('Database initialization completed successfully!');
print('');
print('='.repeat(60));
print('Database: pystrument');
print('Application User: pystrument_user');
print('Demo Project Key: demo_project_001');
print('='.repeat(60));
print('');