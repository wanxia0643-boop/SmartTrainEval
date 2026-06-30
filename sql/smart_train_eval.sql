-- =============================================================================
-- 智训评软件实训智能评价系统 (SmartTrainEval)
-- 数据库建表脚本
-- DB: MySQL 8.0  Engine: InnoDB  Charset: utf8mb4  Collate: utf8mb4_0900_ai_ci
-- 说明:
--   1. 所有表均含 create_time / update_time / is_deleted（逻辑删除）三字段
--   2. 字段下划线命名，主键自增 BIGINT UNSIGNED
--   3. 表结构遵循第三范式，外键关系通过业务索引保证查询性能（默认不建物理外键约束，
--      由应用层维护引用完整性，便于分库分表与历史数据归档；如需强约束可放开末尾注释）
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `smart_train_eval`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE `smart_train_eval`;


-- =============================================================================
-- 表1：角色表 sys_role
-- =============================================================================
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_name`   VARCHAR(50)     NOT NULL                COMMENT '角色名称，如：学生/教师/企业导师/管理员',
    `role_code`   VARCHAR(50)     NOT NULL                COMMENT '角色编码（英文唯一标识），如：STUDENT/TEACHER/ENTERPRISE/ADMIN',
    `data_scope`  TINYINT         NOT NULL DEFAULT 1      COMMENT '数据范围：1-本人 2-本组织 3-全部',
    `description` VARCHAR(255)             DEFAULT NULL   COMMENT '角色描述',
    `sort`        INT             NOT NULL DEFAULT 0      COMMENT '显示排序，越小越靠前',
    `status`      TINYINT         NOT NULL DEFAULT 1      COMMENT '状态：1-启用 0-停用',
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`  TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_code` (`role_code`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户角色表';


-- =============================================================================
-- 表2：组织表 sys_org（学校/学院/班级/企业，树形结构）
-- =============================================================================
DROP TABLE IF EXISTS `sys_org`;
CREATE TABLE `sys_org` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `org_name`    VARCHAR(100)    NOT NULL                COMMENT '组织名称',
    `org_code`    VARCHAR(64)     NOT NULL                COMMENT '组织编码（唯一）',
    `org_type`    TINYINT         NOT NULL DEFAULT 1      COMMENT '组织类型：1-学校 2-学院 3-专业 4-班级 5-企业',
    `parent_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0      COMMENT '父级组织ID，0表示顶级',
    `ancestors`   VARCHAR(500)    NOT NULL DEFAULT ''     COMMENT '祖级路径，逗号分隔，如：0,1,5',
    `leader`      VARCHAR(50)              DEFAULT NULL   COMMENT '负责人姓名',
    `contact`     VARCHAR(30)              DEFAULT NULL   COMMENT '联系电话',
    `sort`        INT             NOT NULL DEFAULT 0      COMMENT '显示排序',
    `status`      TINYINT         NOT NULL DEFAULT 1      COMMENT '状态：1-启用 0-停用',
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`  TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_org_code` (`org_code`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_org_type` (`org_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='组织机构表';


-- =============================================================================
-- 表3：用户表 sys_user
--   通过 role_id 关联 sys_role，org_id 关联 sys_org，满足第三范式（用户表不冗余角色/组织名称）
-- =============================================================================
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username`    VARCHAR(50)     NOT NULL                COMMENT '登录账号（唯一）',
    `password`    VARCHAR(100)    NOT NULL                COMMENT '登录密码（BCrypt加密存储）',
    `real_name`   VARCHAR(50)     NOT NULL                COMMENT '真实姓名',
    `nickname`    VARCHAR(50)              DEFAULT NULL   COMMENT '昵称',
    `role_id`     BIGINT UNSIGNED NOT NULL                COMMENT '角色ID，关联 sys_role.id',
    `org_id`      BIGINT UNSIGNED          DEFAULT NULL   COMMENT '所属组织ID，关联 sys_org.id',
    `student_no`  VARCHAR(50)              DEFAULT NULL   COMMENT '学号/工号',
    `gender`      TINYINT         NOT NULL DEFAULT 0      COMMENT '性别：0-未知 1-男 2-女',
    `email`       VARCHAR(100)             DEFAULT NULL   COMMENT '邮箱',
    `phone`       VARCHAR(30)              DEFAULT NULL   COMMENT '手机号',
    `avatar`      VARCHAR(255)             DEFAULT NULL   COMMENT '头像URL',
    `status`      TINYINT         NOT NULL DEFAULT 1      COMMENT '状态：1-正常 0-禁用',
    `last_login_time` DATETIME             DEFAULT NULL   COMMENT '最后登录时间',
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`  TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_role_id` (`role_id`),
    KEY `idx_org_id` (`org_id`),
    KEY `idx_student_no` (`student_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';


-- =============================================================================
-- 表4：实训项目表 train_project
-- =============================================================================
DROP TABLE IF EXISTS `train_project`;
CREATE TABLE `train_project` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `project_name`  VARCHAR(150)    NOT NULL                COMMENT '项目名称',
    `project_code`  VARCHAR(64)     NOT NULL                COMMENT '项目编码（唯一）',
    `org_id`        BIGINT UNSIGNED          DEFAULT NULL   COMMENT '归属组织ID，关联 sys_org.id',
    `teacher_id`    BIGINT UNSIGNED NOT NULL                COMMENT '负责教师ID，关联 sys_user.id',
    `enterprise_id` BIGINT UNSIGNED          DEFAULT NULL   COMMENT '企业导师ID，关联 sys_user.id',
    `category`      VARCHAR(50)              DEFAULT NULL   COMMENT '项目类别，如：软件开发/网络运维/数据分析',
    `difficulty`    TINYINT         NOT NULL DEFAULT 2      COMMENT '难度：1-初级 2-中级 3-高级',
    `description`   TEXT                     DEFAULT NULL   COMMENT '项目描述与实训要求',
    `start_time`    DATETIME                 DEFAULT NULL   COMMENT '开始时间',
    `end_time`      DATETIME                 DEFAULT NULL   COMMENT '结束时间',
    `status`        TINYINT         NOT NULL DEFAULT 0      COMMENT '状态：0-未开始 1-进行中 2-已结束 3-已归档',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`    TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_project_code` (`project_code`),
    KEY `idx_teacher_id` (`teacher_id`),
    KEY `idx_enterprise_id` (`enterprise_id`),
    KEY `idx_org_id` (`org_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='实训项目表';


-- =============================================================================
-- 表5：实训成果表 train_achievement（学生针对项目提交的成果）
-- =============================================================================
DROP TABLE IF EXISTS `train_achievement`;
CREATE TABLE `train_achievement` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `project_id`    BIGINT UNSIGNED NOT NULL                COMMENT '所属实训项目ID，关联 train_project.id',
    `student_id`    BIGINT UNSIGNED NOT NULL                COMMENT '提交学生ID，关联 sys_user.id',
    `title`         VARCHAR(200)    NOT NULL                COMMENT '成果标题',
    `content`       LONGTEXT                 DEFAULT NULL   COMMENT '成果文本内容（报告/代码说明等）',
    `attachment_url` VARCHAR(500)            DEFAULT NULL   COMMENT '附件URL（压缩包/文档/视频）',
    `repo_url`      VARCHAR(255)             DEFAULT NULL   COMMENT '代码仓库地址',
    `version`       INT             NOT NULL DEFAULT 1      COMMENT '提交版本号',
    `submit_time`   DATETIME                 DEFAULT NULL   COMMENT '提交时间',
    `status`        TINYINT         NOT NULL DEFAULT 0      COMMENT '状态：0-草稿 1-已提交 2-评价中 3-已评价 4-退回重做',
    `final_score`   DECIMAL(6,2)             DEFAULT NULL   COMMENT '最终综合得分（评价结果汇总后回填）',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`    TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_project_id` (`project_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_status` (`status`),
    KEY `idx_project_student` (`project_id`, `student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='实训成果表';


-- =============================================================================
-- 表6：评价指标表 eval_indicator（支持按项目配置的多级指标体系）
-- =============================================================================
DROP TABLE IF EXISTS `eval_indicator`;
CREATE TABLE `eval_indicator` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `project_id`     BIGINT UNSIGNED          DEFAULT NULL   COMMENT '所属项目ID，关联 train_project.id；NULL表示通用模板指标',
    `parent_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0      COMMENT '父级指标ID，0表示一级指标',
    `indicator_name` VARCHAR(100)    NOT NULL                COMMENT '指标名称，如：代码规范性/功能完整性',
    `indicator_code` VARCHAR(64)     NOT NULL                COMMENT '指标编码（项目内唯一）',
    `weight`         DECIMAL(5,2)    NOT NULL DEFAULT 0.00   COMMENT '权重（百分比，同级合计应为100）',
    `max_score`      DECIMAL(6,2)    NOT NULL DEFAULT 100.00 COMMENT '满分值',
    `scoring_rule`   VARCHAR(1000)            DEFAULT NULL   COMMENT '评分标准/评分细则（供大模型与人工参考）',
    `sort`           INT             NOT NULL DEFAULT 0      COMMENT '显示排序',
    `status`         TINYINT         NOT NULL DEFAULT 1      COMMENT '状态：1-启用 0-停用',
    `create_time`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`     TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_project_id` (`project_id`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_indicator_code` (`indicator_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='评价指标表';


-- =============================================================================
-- 表7：评价结果表 eval_result（某成果在某指标上的一次评分，支持AI与人工）
-- =============================================================================
DROP TABLE IF EXISTS `eval_result`;
CREATE TABLE `eval_result` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `achievement_id` BIGINT UNSIGNED NOT NULL                COMMENT '实训成果ID，关联 train_achievement.id',
    `indicator_id`   BIGINT UNSIGNED NOT NULL                COMMENT '评价指标ID，关联 eval_indicator.id',
    `eval_type`      TINYINT         NOT NULL DEFAULT 1      COMMENT '评价方式：1-大模型AI评价 2-教师评价 3-企业导师评价 4-学生自评',
    `evaluator_id`   BIGINT UNSIGNED          DEFAULT NULL   COMMENT '评价人ID（人工评价时关联 sys_user.id；AI评价为NULL）',
    `llm_log_id`     BIGINT UNSIGNED          DEFAULT NULL   COMMENT '大模型调用日志ID，关联 llm_call_log.id（AI评价时记录）',
    `score`          DECIMAL(6,2)    NOT NULL DEFAULT 0.00   COMMENT '该指标得分',
    `comment`        TEXT                     DEFAULT NULL   COMMENT '评语/评价意见',
    `suggestion`     TEXT                     DEFAULT NULL   COMMENT '改进建议',
    `eval_time`      DATETIME                 DEFAULT NULL   COMMENT '评价时间',
    `create_time`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`     TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_achievement_id` (`achievement_id`),
    KEY `idx_indicator_id` (`indicator_id`),
    KEY `idx_evaluator_id` (`evaluator_id`),
    KEY `idx_eval_type` (`eval_type`),
    KEY `idx_achievement_indicator` (`achievement_id`, `indicator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='评价结果表';


-- =============================================================================
-- 表8：大模型调用日志表 llm_call_log
-- =============================================================================
DROP TABLE IF EXISTS `llm_call_log`;
CREATE TABLE `llm_call_log` (
    `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id`           BIGINT UNSIGNED          DEFAULT NULL   COMMENT '触发调用的用户ID，关联 sys_user.id',
    `biz_type`          VARCHAR(50)              DEFAULT NULL   COMMENT '业务类型，如：ACHIEVEMENT_EVAL/REPORT_GEN/CHAT',
    `biz_id`            BIGINT UNSIGNED          DEFAULT NULL   COMMENT '关联业务主键ID（如成果ID）',
    `model_name`        VARCHAR(80)     NOT NULL                COMMENT '模型名称，如：claude-opus-4-8',
    `request_id`        VARCHAR(80)              DEFAULT NULL   COMMENT '上游请求ID（用于追踪）',
    `prompt_text`       LONGTEXT                 DEFAULT NULL   COMMENT '请求提示词内容',
    `response_text`     LONGTEXT                 DEFAULT NULL   COMMENT '模型返回内容',
    `prompt_tokens`     INT             NOT NULL DEFAULT 0      COMMENT '输入token数',
    `completion_tokens` INT             NOT NULL DEFAULT 0      COMMENT '输出token数',
    `total_tokens`      INT             NOT NULL DEFAULT 0      COMMENT '总token数',
    `cost`              DECIMAL(10,4)   NOT NULL DEFAULT 0.0000 COMMENT '调用费用（元）',
    `duration_ms`       INT             NOT NULL DEFAULT 0      COMMENT '调用耗时（毫秒）',
    `status`            TINYINT         NOT NULL DEFAULT 1      COMMENT '调用状态：1-成功 0-失败',
    `error_msg`         VARCHAR(1000)            DEFAULT NULL   COMMENT '失败原因',
    `create_time`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`        TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_biz` (`biz_type`, `biz_id`),
    KEY `idx_model_name` (`model_name`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='大模型调用日志表';


-- =============================================================================
-- 表9：报表记录表 report_record
-- =============================================================================
DROP TABLE IF EXISTS `report_record`;
CREATE TABLE `report_record` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `report_name`   VARCHAR(150)    NOT NULL                COMMENT '报表名称',
    `report_type`   TINYINT         NOT NULL DEFAULT 1      COMMENT '报表类型：1-学生成绩报表 2-项目评价报表 3-组织汇总报表 4-AI使用统计报表',
    `project_id`    BIGINT UNSIGNED          DEFAULT NULL   COMMENT '关联项目ID，关联 train_project.id',
    `org_id`        BIGINT UNSIGNED          DEFAULT NULL   COMMENT '关联组织ID，关联 sys_org.id',
    `generator_id`  BIGINT UNSIGNED NOT NULL                COMMENT '生成人ID，关联 sys_user.id',
    `file_format`   VARCHAR(20)     NOT NULL DEFAULT 'PDF'  COMMENT '文件格式：PDF/EXCEL/WORD',
    `file_url`      VARCHAR(500)             DEFAULT NULL   COMMENT '报表文件URL',
    `params`        JSON                     DEFAULT NULL   COMMENT '生成参数（查询条件快照，JSON）',
    `status`        TINYINT         NOT NULL DEFAULT 0      COMMENT '状态：0-生成中 1-成功 2-失败',
    `remark`        VARCHAR(500)             DEFAULT NULL   COMMENT '备注',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP                          COMMENT '创建时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted`    TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除：0-未删除 1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_report_type` (`report_type`),
    KEY `idx_project_id` (`project_id`),
    KEY `idx_generator_id` (`generator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='报表记录表';


-- =============================================================================
-- 初始化基础角色数据
-- 注：需求文本写“3条”，但列举了 学生/教师/企业导师/管理员 共4个角色，此处按4个完整初始化
-- =============================================================================
INSERT INTO `sys_role` (`role_name`, `role_code`, `data_scope`, `description`, `sort`, `status`) VALUES
('学生',   'STUDENT', 1, '提交实训成果、查看个人评价与报告', 1, 1),
('教师',   'TEACHER', 2, '管理实训项目、配置评价指标、审核与人工评价', 2, 1),
('企业导师', 'ENTERPRISE', 2, '参与企业侧实训成果评价与指导', 3, 1),
('管理员',  'ADMIN',   3, '系统管理、组织与用户管理、全局数据维护', 4, 1);


-- =============================================================================
-- （可选）物理外键约束 —— 默认注释，按需放开
-- =============================================================================
-- ALTER TABLE `sys_user`         ADD CONSTRAINT `fk_user_role`      FOREIGN KEY (`role_id`)        REFERENCES `sys_role`(`id`);
-- ALTER TABLE `sys_user`         ADD CONSTRAINT `fk_user_org`       FOREIGN KEY (`org_id`)         REFERENCES `sys_org`(`id`);
-- ALTER TABLE `train_project`    ADD CONSTRAINT `fk_proj_teacher`   FOREIGN KEY (`teacher_id`)     REFERENCES `sys_user`(`id`);
-- ALTER TABLE `train_project`    ADD CONSTRAINT `fk_proj_enterprise` FOREIGN KEY (`enterprise_id`)  REFERENCES `sys_user`(`id`);
-- ALTER TABLE `train_achievement`ADD CONSTRAINT `fk_ach_project`    FOREIGN KEY (`project_id`)     REFERENCES `train_project`(`id`);
-- ALTER TABLE `train_achievement`ADD CONSTRAINT `fk_ach_student`    FOREIGN KEY (`student_id`)     REFERENCES `sys_user`(`id`);
-- ALTER TABLE `eval_indicator`   ADD CONSTRAINT `fk_ind_project`    FOREIGN KEY (`project_id`)     REFERENCES `train_project`(`id`);
-- ALTER TABLE `eval_result`      ADD CONSTRAINT `fk_res_ach`        FOREIGN KEY (`achievement_id`) REFERENCES `train_achievement`(`id`);
-- ALTER TABLE `eval_result`      ADD CONSTRAINT `fk_res_indicator`  FOREIGN KEY (`indicator_id`)   REFERENCES `eval_indicator`(`id`);
-- ALTER TABLE `eval_result`      ADD CONSTRAINT `fk_res_llmlog`     FOREIGN KEY (`llm_log_id`)     REFERENCES `llm_call_log`(`id`);
