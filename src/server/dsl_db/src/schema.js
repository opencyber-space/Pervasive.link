const mongoose = require('mongoose');

const moduleSchema = new mongoose.Schema({
    codePath: { type: String, default: "" },
    settings: { type: Object, default: {} },
    parameters: { type: Object, default: {} },
    name: { type: String, required: true },
    description: { type: String, required: true },
    tags: { type: [String], default: [] },
    resource_requirements: { type: Object, default: {} }
});

const versionSchema = new mongoose.Schema({
    releaseTag: { type: String, required: true },
    version: { type: String, required: true }
})

const workflowSchema = new mongoose.Schema({
    workflow_id: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    version: { type: versionSchema, required: true },
    description: { type: String, required: true },
    tags: { type: [String], default: [] },
    globalSettings: { type: Object, default: {} },
    globalParameters: { type: Object, default: {} },
    modules: { type: Map, of: moduleSchema },
    graph: { type: Object, default: {} }
}, { _id: false });

module.exports = mongoose.model('Workflow', workflowSchema);
