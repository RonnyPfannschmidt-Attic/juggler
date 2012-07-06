Backbone.sync = (method, model, success, error) -> success()


class CouchModel extends Backbone.Model
  idAttribute: "_id"


class CouchCollection extends Backbone.Collection
  model: CouchModel

class StatusCollection extends CouchCollection
  comparator: (item) ->
    driver = item.get 'driver'
    if driver
      "#{driver} #{item.id}"
    else
      item.id


class StatusView extends Backbone.View
  tagName: 'li'

  render: =>
    @$el.html @model.id
    if @model.get 'driver'
      @$el.addClass 'driver'
    else
      @$el.addClass 'worker'
    return @

class StatusCollectionView extends Backbone.View

  initialize: =>

    @collection = new StatusCollection
    @collection.bind 'add', @appendItem
    @collection.bind 'reset', @render
    @render()

    @changes = db.changes '0', 
      include_docs: 'true'
      filter: "_view"
      view: 'juggler/status'
    @changes.onChange (changes) => @add_changes changes


  add_changes: (changes) ->
    push = []
    for item in changes.results
      log.info 'change ' + JSON.stringify item
      if item.deleted
        item = @collection.get(item.id)
        if item != undefined
          @collection.remove(item)
          item.view?.$el.remove()
      else
        @collection.add item.doc, merge: yes
    return true

  render: () =>
    @$el.empty()
    @collection.forEach (item) =>
      @$el.append(item.view.$el)
    @

  appendItem: (item) =>
    view = new StatusView model: item
    item.view = view
    el = view.render().$el
    index = @collection.indexOf(item)
    if index == @collection.length-1

      @$el.append(el)
    else
      view = @collection.at(index+1)?.view
      if view != undefined
        el.insertBefore(view.$el)
      else
        @$el.append(el)


status_add = ->
  db.bulkSave {
    docs: [
      {_id: 'fun',  type: 'juggler:warden'},
      {_id: 'bee',  type: 'juggler:worker', warden: 'fun'},
      {_id: 'fun2', type: 'juggler:warden'},
      {_id: 'bee2', type: 'juggler:worker', warden: 'fun'},
      {_id: 'bee3', type: 'juggler:worker', warden: 'fun2'}
    ]
    },
    success: (data) -> log.info "added\n" + JSON.stringify data

status_remove = ->
    docs = ["fun", "fun2", "bee", "bee2", "bee3"]
    db.allDocs
      keys: docs
      include_docs: yes
      success: (res) ->
        remove = for row in res.rows
          if not row.value._deleted
            {_id: row.id, _rev: row.value.rev}
        db.bulkRemove {docs: remove} , success: (delres) ->
          log.info "done\n" +JSON.stringify delres
