import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const asAiService = {
    // Datasets
    uploadDataset: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/upload_dataset', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    getDatasetInsights: async () => {
        return api.get('/dataset_insights');
    },

    // AI Chat & Multi-Agent
    askQuestion: async (query) => {
        return api.post('/ask', { query });
    },

    multiAgentAnalysis: async () => {
        return api.get('/multi_agent_analysis');
    },

    // Dashboards
    generateDashboard: async () => {
        return api.get('/generate_dashboard');
    },

    // Models & Lab
    trainModel: async (datasetId, targetColumn) => {
        return api.post('/train_model', {
            dataset_id: datasetId,
            target_column: targetColumn,
        });
    },

    monitorModel: async (datasetId, newDatasetId) => {
        return api.post('/monitor_model', {
            dataset_id: datasetId,
            new_dataset: newDatasetId,
        });
    },

    // Memory & Insights
    getAiMemory: async () => {
        return api.get('/ai_memory');
    },

    submitFeedback: async (analysisId, rating) => {
        return api.post('/analysis_feedback', {
            analysis_id: analysisId,
            rating,
        });
    },

    getAiAnalysis: async (report = false) => {
        return api.get(`/ai_analysis${report ? '?report=true' : ''}`);
    },

    // Streaming
    startStream: async (topicName) => {
        return api.post('/start_stream', { topic_name: topicName });
    },

    getStreamStatus: async () => {
        return api.get('/stream_status');
    },

    // Reports
    generateReport: async (datasetId) => {
        return api.post('/generate_report', { dataset_id: datasetId });
    },
};

export default api;
