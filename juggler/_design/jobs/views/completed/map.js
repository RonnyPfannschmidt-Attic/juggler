function(doc) {
    if (doc.doc_type == "Job" && doc.status == "completed") {
        emit([doc.project, doc.build, doc._id], doc);
    }
}
