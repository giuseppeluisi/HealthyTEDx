const connect_to_db = require('./db');

// GET BY TALK HANDLER

const Feedback = require('./Feedback');

module.exports.get_talks_by_feedback = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));
    let body = {}
    if (event.body) {
        body = JSON.parse(event.body)
    }
    const { _id, feedback_text, valutazione } = body;
    
    // set default
    if (!_id || !feedback_text || typeof valutazione !== 'number') {
        callback(null, {
                    statusCode: 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Invalid input data.'
        })
    }
    await connect_to_db();
    
    const newFeedback = new Feedback({
        _id,
        feedback_text,
        valutazione
    });

    try {
        const result = await newFeedback.save();
        callback(null, {
            statusCode: 200,
            body: JSON.stringify('Feedback ricevuto con successo!')
        });
    } catch (error) {
        console.error('Errore:', error);
        callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'text/plain' },
            body: 'Errore nel salvataggio del feedback.'
        });
    }

};
