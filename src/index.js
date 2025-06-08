#!/usr/bin/env node

/**
 * OpenDevinAI520 - 实用工具开发平台
 * Node.js 主程序入口文件
 * 
 * 人人为我，我为人人 - 让我们一起构建更好的开发工具生态！
 */

const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务
app.use(express.static('public'));

// 路由
app.get('/', (req, res) => {
    res.json({
        name: 'OpenDevinAI520',
        description: '实用工具开发平台 - 自用人人为我我为人人',
        version: '1.0.0',
        message: '欢迎使用 OpenDevinAI520！',
        endpoints: {
            '/': '主页',
            '/api/tools': '获取工具列表',
            '/api/health': '健康检查'
        }
    });
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.get('/api/tools', (req, res) => {
    res.json({
        tools: [
            {
                name: '代码格式化工具',
                status: '开发中',
                description: '自动格式化各种编程语言的代码'
            },
            {
                name: '文件批量处理工具',
                status: '开发中',
                description: '批量处理文件的重命名、转换等操作'
            },
            {
                name: 'API测试工具',
                status: '开发中',
                description: '快速测试和调试API接口'
            },
            {
                name: '数据转换工具',
                status: '开发中',
                description: '各种数据格式之间的转换'
            },
            {
                name: '开发环境配置工具',
                status: '开发中',
                description: '快速配置开发环境'
            },
            {
                name: '日志分析工具',
                status: '开发中',
                description: '分析和可视化日志文件'
            }
        ],
        message: '更多工具正在开发中，敬请期待！'
    });
});

// 404 处理
app.use('*', (req, res) => {
    res.status(404).json({
        error: '页面未找到',
        message: '请检查您的请求路径'
    });
});

// 错误处理
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: '服务器内部错误',
        message: '请稍后重试'
    });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`
🚀 OpenDevinAI520 服务器已启动！
📍 地址: http://localhost:${PORT}
🎯 人人为我，我为人人 - 让我们一起构建更好的开发工具生态！
    `);
});

module.exports = app;