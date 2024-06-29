const mongoose = require('mongoose');

const talk_schema = new mongoose.Schema({
    _id: String,
    id_related: String,
    slug: String,
    speakers: String,
    title: String,
    url: String,
    description: String,
    duration: String,
    publishedAt: String,
    image_url: String,
    id_related_video: Array,
    title_related_video: Array,
    tags: Array
}, { collection: 'tedx_data_1' });

module.exports = mongoose.model('talk', talk_schema);
