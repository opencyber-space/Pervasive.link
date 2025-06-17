const express = require('express');
const mongoose = require('mongoose');
const Workflow = require('./src/schema');
const app = express();
require('dotenv').config();

app.use(express.json());

mongoose.connect(process.env.DB_URL, {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log('Database connected'))
    .catch(err => console.error('Database connection error:', err));

// Get all workflows
app.get('/workflows', async (req, res) => {
    try {
        const workflows = await Workflow.find();
        res.status(200).json({ success: true, data: workflows });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
});

// Get a workflow by workflow_id
app.get('/workflows/:workflow_id', async (req, res) => {
    try {
        const workflow = await Workflow.findOne({ workflow_id: req.params.workflow_id });
        if (!workflow) return res.status(404).json({ success: false, message: 'Workflow not found' });
        res.status(200).json({ success: true, data: workflow });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
});

// Create a new workflow
app.post('/workflows', async (req, res) => {
    try {

        const workflow_id = req.body.name + ":" + req.body.version.version + "-" + req.body.version.releaseTag;
        req.body.workflow_id = workflow_id;

        const workflow = new Workflow(req.body);
        const savedWorkflow = await workflow.save();
        res.status(200).json({ success: true, data: savedWorkflow });
    } catch (err) {
        res.status(400).json({ success: false, message: err.message });
    }
});

// Update a workflow by workflow_id
app.put('/workflows/:workflow_id', async (req, res) => {
    try {
        const updatedWorkflow = await Workflow.findOneAndUpdate(
            { workflow_id: req.params.workflow_id },
            req.body,
            { new: true, runValidators: true }
        );
        if (!updatedWorkflow) return res.status(404).json({ success: false, message: 'Workflow not found' });
        res.status(200).json({ success: true, data: updatedWorkflow });
    } catch (err) {
        res.status(400).json({ success: false, message: err.message });
    }
});

// Delete a workflow by workflow_id
app.delete('/workflows/:workflow_id', async (req, res) => {
    try {
        const deletedWorkflow = await Workflow.findOneAndDelete({ workflow_id: req.params.workflow_id });
        if (!deletedWorkflow) return res.status(404).json({ success: false, message: 'Workflow not found' });
        res.status(200).json({ success: true, data: deletedWorkflow });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
});

app.post('/workflows/query', async (req, res) => {
    try {
        const query = req.body.query || {};
        const projection = req.body.projection || null;
        const limit = parseInt(req.body.limit) || 100;
        const skip = parseInt(req.body.skip) || 0;
        const sort = req.body.sort || {};

        const workflows = await Workflow.find(query, projection)
            .skip(skip)
            .limit(limit)
            .sort(sort);

        res.status(200).json({ success: true, data: workflows });
    } catch (err) {
        res.status(400).json({ success: false, message: err.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
