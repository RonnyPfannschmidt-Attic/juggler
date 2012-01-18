
function(doc) {
    if (doc.doc_type == "Job") {
        emit([doc.project, doc.build, doc._id], doc);
    }
}
