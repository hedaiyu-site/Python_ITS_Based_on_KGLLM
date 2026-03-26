-- 个性化学习路径系统数据库表结构

-- 1. 修改用户表，增加学习路径字段
ALTER TABLE users ADD COLUMN learning_path VARCHAR(20) DEFAULT 'basic' COMMENT '学习路径: basic, advanced, basic_to_advanced';

-- 2. 用户学习档案表
CREATE TABLE IF NOT EXISTS user_learning_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    learning_path VARCHAR(20) NOT NULL DEFAULT 'basic' COMMENT '学习路径: basic, advanced, basic_to_advanced',
    current_level VARCHAR(20) DEFAULT 'beginner' COMMENT '当前水平',
    total_study_time INT DEFAULT 0 COMMENT '总学习时间(分钟)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户学习档案表';

-- 3. 知识点进度表
CREATE TABLE IF NOT EXISTS knowledge_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    knowledge_point_id VARCHAR(100) NOT NULL COMMENT '知识点ID',
    knowledge_point_name VARCHAR(255) NOT NULL COMMENT '知识点名称',
    course_type VARCHAR(20) COMMENT '所属课程: basic, advanced',
    chapter_name VARCHAR(255) COMMENT '所属章节',
    section_name VARCHAR(255) COMMENT '所属小节',
    status ENUM('not_started', 'learning', 'mastered', 'reviewing') DEFAULT 'not_started',
    mastery_level INT DEFAULT 0 COMMENT '掌握程度 0-100',
    quiz_score FLOAT DEFAULT 0 COMMENT '测验得分',
    quiz_count INT DEFAULT 0 COMMENT '测验次数',
    correct_count INT DEFAULT 0 COMMENT '答对次数',
    last_study_time TIMESTAMP NULL COMMENT '最后学习时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_kp (user_id, knowledge_point_id),
    INDEX idx_user_status (user_id, status),
    INDEX idx_mastery (user_id, mastery_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点进度表';

-- 如果表已存在，添加 section_name 字段
-- ALTER TABLE knowledge_progress ADD COLUMN section_name VARCHAR(255) COMMENT '所属小节' AFTER chapter_name;

-- 4. 测验题目表
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    knowledge_point_id VARCHAR(100) NOT NULL COMMENT '知识点ID',
    knowledge_point_name VARCHAR(255) NOT NULL COMMENT '知识点名称',
    question TEXT NOT NULL COMMENT '题目内容',
    option_a TEXT NOT NULL COMMENT '选项A',
    option_b TEXT NOT NULL COMMENT '选项B',
    option_c TEXT NOT NULL COMMENT '选项C',
    option_d TEXT NOT NULL COMMENT '选项D',
    correct_answer CHAR(1) NOT NULL COMMENT '正确答案: A, B, C, D',
    explanation TEXT COMMENT '答案解析',
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium' COMMENT '难度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kp (knowledge_point_id),
    INDEX idx_difficulty (difficulty)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测验题目表';

-- 5. 用户测验记录表
CREATE TABLE IF NOT EXISTS user_quiz_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    knowledge_point_id VARCHAR(100) NOT NULL,
    question_id INT NOT NULL,
    user_answer CHAR(1) NOT NULL COMMENT '用户答案',
    is_correct BOOLEAN NOT NULL COMMENT '是否正确',
    quiz_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE,
    INDEX idx_user_kp (user_id, knowledge_point_id),
    INDEX idx_quiz_time (quiz_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户测验记录表';

-- 6. 学习路径配置表
CREATE TABLE IF NOT EXISTS learning_path_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path_type VARCHAR(20) NOT NULL UNIQUE COMMENT '路径类型: basic, advanced, basic_to_advanced',
    path_name VARCHAR(100) NOT NULL COMMENT '路径名称',
    description TEXT COMMENT '路径描述',
    course_ids JSON COMMENT '包含的课程ID列表',
    estimated_days INT COMMENT '预计学习天数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习路径配置表';

-- 插入默认学习路径配置
INSERT INTO learning_path_configs (path_type, path_name, description, course_ids, estimated_days) VALUES
('basic', '基础学习路径', '适合初学者，掌握Python基础语法和核心概念', '["course_basic"]', 30),
('advanced', '高级学习路径', '适合有基础的学习者，深入学习高级特性', '["course_advanced"]', 45),
('basic_to_advanced', '完整学习路径', '从基础到高级的完整学习路径', '["course_basic", "course_advanced"]', 75);
