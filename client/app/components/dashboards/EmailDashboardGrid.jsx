import React from "react";
import PropTypes from "prop-types";
import {chain, cloneDeep, find} from "lodash";
import cx from "classnames";
import {Responsive, WidthProvider} from "react-grid-layout";
import {VisualizationWidget, TextboxWidget, RestrictedWidget} from "@/components/dashboards/dashboard-widget";
import {FiltersType} from "@/components/Filters";
import cfg from "@/config/dashboard-grid-options";
import AutoHeightController from "./AutoHeightController";
import DashboardGrid from "./DashboardGrid.jsx";
import {WidgetTypeEnum} from "@/services/widget";

import "react-grid-layout/css/styles.css";
import "./dashboard-grid.less";

const ResponsiveGridLayout = WidthProvider(Responsive);

const WidgetType = PropTypes.shape({
  id: PropTypes.number.isRequired,
  options: PropTypes.shape({
    position: PropTypes.shape({
      col: PropTypes.number.isRequired,
      row: PropTypes.number.isRequired,
      sizeY: PropTypes.number.isRequired,
      minSizeY: PropTypes.number.isRequired,
      maxSizeY: PropTypes.number.isRequired,
      sizeX: PropTypes.number.isRequired,
      minSizeX: PropTypes.number.isRequired,
      maxSizeX: PropTypes.number.isRequired,
    }).isRequired,
  }).isRequired,
});

const SINGLE = "single-column";
const MULTI = "multi-column";

const EmailDashboardWidget = React.memo(
  function EmailDashboardWidget({
                                  widget,
                                  dashboard,
                                  onLoadWidget,
                                  onRefreshWidget,
                                  onRemoveWidget,
                                  onParameterMappingsChange,
                                  isEditing,
                                  canEdit,
                                  isPublic,
                                  isLoading,
                                  filters,
                                  tableLayout,
                                }) {
    const {type} = widget;
    const onLoad = () => onLoadWidget(widget);
    const onRefresh = () => onRefreshWidget(widget);
    const onDelete = () => onRemoveWidget(widget.id);

    if (type === WidgetTypeEnum.VISUALIZATION) {
      return (
        <VisualizationWidget
          widget={widget}
          tableLayout={tableLayout}
          dashboard={dashboard}
          filters={filters}
          isEditing={isEditing}
          canEdit={canEdit}
          isPublic={isPublic}
          isLoading={isLoading}
          onLoad={onLoad}
          onRefresh={onRefresh}
          onDelete={onDelete}
          onParameterMappingsChange={onParameterMappingsChange}
        />
      );
    }
    if (type === WidgetTypeEnum.TEXTBOX) {
      return <TextboxWidget widget={widget} tableLayout={tableLayout} canEdit={canEdit} isPublic={isPublic} onDelete={onDelete}/>;
    }
    return <RestrictedWidget widget={widget} tableLayout={tableLayout}  />;
  },
  (prevProps, nextProps) =>
    prevProps.widget === nextProps.widget &&
    prevProps.canEdit === nextProps.canEdit &&
    prevProps.isPublic === nextProps.isPublic &&
    prevProps.isLoading === nextProps.isLoading &&
    prevProps.filters === nextProps.filters &&
    prevProps.isEditing === nextProps.isEditing
);

function min(x, y ) {
  return x > y ? y : x;
}

class TableLayout extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    let props = this.props;
    let child = props.children
    let widgets = props.widgets
    let rowHeight = props.rowHeight;
    if (!child || child.length === 0) {
      return null
    }
    let keyMap = {}
    for (let i = 0; i < child.length; i++) {
      keyMap[child[i].key] = child[i]
      //layout.push(child[i])
    }

    if (!props.layouts) {
      return null
    }
    let layout = props.layouts
    console.log("get layout",layout)
    let rows = []
    while (layout.length > 0) {
      let min_y = layout[0].y;
      let max_height = layout[0].h;
      for (let i = 1; i < layout.length; i++) {
        min_y = min(min_y, layout[i].y)
      }
      let cols = []
      let remain = []
      for (let i = 0; i < layout.length; i++) {
        if (layout[i].y === min_y) {
          cols.push(layout[i])
          if(layout[i].h>max_height){
            max_height=layout[i].h
          }
        } else {
          remain.push(layout[i])
        }
      }
      cols.sort((a,b)=>{
        return a.x>b.x
      })
      for (let i = 0; i < cols.length; i++) {
        if(i===0){
          if(cols[i].x>0){
            cols.splice(i,0,{
              x:0,
              h:max_height,
              w:cols[i].x,
            })
          }
        }else {
          if(cols[i].x>cols[i-1].x+cols[i-1].w){
            cols.splice(i,0,{
              x:cols[i-1].x+cols[i-1].w,
              w:cols[i].x-(cols[i-1].x+cols[i-1].w),
            })
          }
        }
      }
      layout = remain
      rows.push(cols)
      for (let i = 0; i < max_height-1; i++) {
        rows.push([])
      }

    }
    //console.log("sort rows", JSON.stringify(rows))

    let th =[]
    for (let i = 0; i < 6; i++) {
      th.push(
        (<td key={"td"+i} width={(100.0/6)+'%'}>{i}</td>)
      )
    }

    //rowHeight
    return (
      <table width={1020} className={"email-table-layout"} id="table_width">
        <thead>
          <th width={170}></th>
          <th width={170}></th>
          <th width={170}></th>
          <th width={170}></th>
          <th width={170}></th>
          <th width={170}></th>
        </thead>
        <tbody>
        {
          rows.map((cols,rowIndex)=>{
            return (<tr key={'row-'+rowIndex}>

              {cols.map((col,colIndex)=>{
                return (
                  <td key={'col'+colIndex} colSpan={col.w} rowSpan={col.h} >
                    {keyMap[col.i]?keyMap[col.i]:null}
                  </td>
                )
              })}
            </tr>)
          })
        }
        </tbody>
      </table>
    )

  }
}

class EmailDashboardGrid extends DashboardGrid {

  constructor(props) {
    super(props);



    // init AutoHeightController
    this.autoHeightCtrl = new AutoHeightController(this.onWidgetHeightUpdated);
    this.autoHeightCtrl.update(this.props.widgets);
    this.autoHeightCtrl.start()

    let layouts = this.props.widgets.map((widget) => {
      return DashboardGrid.normalizeFrom(widget)
    })

    console.log('widgets constructor layouts', layouts)
    this.state = {
        layouts: layouts,
      };
    }

  componentDidUpdate() {
    // update, in case widgets added or removed
    this.autoHeightCtrl.update(this.props.widgets);
  }

  componentWillUnmount() {
    this.autoHeightCtrl.destroy();
  }

  onWidgetHeightUpdated = (widgetId, newHeight) => {
    super.onWidgetHeightUpdated(widgetId, newHeight);
    console.log("checkHeightChanges onWidgetHeightUpdated",widgetId, newHeight)
  }
  render() {
    const {
      onLoadWidget,
      onRefreshWidget,
      onRemoveWidget,
      onParameterMappingsChange,
      filters,
      dashboard,
      isPublic,
      isEditing,
      widgets,
    } = this.props;
    const className = cx("dashboard-wrapper", isEditing ? "editing-mode" : "preview-mode");



    return (
      <div className={className}>

        <TableLayout
          draggableCancel="input,.sortable-container"
          className={cx("layout", {"disable-animations": this.state.disableAnimations})}
          cols={{[MULTI]: cfg.columns, [SINGLE]: 1}}
          rowHeight={cfg.rowHeight - cfg.margins}
          margin={[cfg.margins, cfg.margins]}
          isDraggable={isEditing}
          isResizable={isEditing}
          widgets={widgets}
          onResizeStart={this.autoHeightCtrl.stop}
          onResizeStop={this.onWidgetResize}
          layouts={this.state.layouts}
          onLayoutChange={this.onLayoutChange}
          onBreakpointChange={this.onBreakpointChange}
          breakpoints={{[MULTI]: cfg.mobileBreakPoint, [SINGLE]: 0}}>
          {widgets.map(widget => (
            <div
              key={widget.id}
              data-grid={DashboardGrid.normalizeFrom(widget)}
              data-widgetid={widget.id}
              style={{
                "position":"static!important",
                "margin": cfg.margins/2,
                'height':(cfg.rowHeight )*widget.options.position.sizeY - cfg.margins
              }}
              data-test={`WidgetId${widget.id}`}
              className={cx("dashboard-widget-wrapper", {
                "widget-auto-height-enabled": this.autoHeightCtrl.exists(widget.id),
              })}>
              <EmailDashboardWidget
                tableLayout={true}
                dashboard={dashboard}
                widget={widget}
                filters={filters}
                isPublic={isPublic}
                isLoading={widget.loading}
                isEditing={false}
                canEdit={false}
                onLoadWidget={onLoadWidget}
                onRefreshWidget={onRefreshWidget}
                onRemoveWidget={onRemoveWidget}
                onParameterMappingsChange={onParameterMappingsChange}
              />
            </div>
          ))}
        </TableLayout>
      </div>
    );
  }
}

export default EmailDashboardGrid;
