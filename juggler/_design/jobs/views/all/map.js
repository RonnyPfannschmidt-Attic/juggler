function(doc) {
    if (doc.doc_type == "Job") {
        emit(doc._id, doc);
    }
}
