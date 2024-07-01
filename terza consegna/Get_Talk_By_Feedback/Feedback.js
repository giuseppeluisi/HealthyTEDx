const mongoose = require('mongoose');

const feedback_schema = new mongoose.Schema({
    _id:  String,
    feedback_text:String, 
    valutazione: Number
}, { collection: 'tedx_feedback' });

module.exports = mongoose.model('Feedback', feedback_schema);
