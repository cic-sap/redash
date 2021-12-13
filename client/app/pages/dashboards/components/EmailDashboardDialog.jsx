import {replace} from "lodash";
import React from "react";
import {axios} from "@/services/axios";
import PropTypes from "prop-types";
import Switch from "antd/lib/switch";
import Modal from "antd/lib/modal";
import Form from "antd/lib/form";
import Input from "antd/lib/input";
import Button from "antd/lib/button";
import { PlusCircleOutlined,ExclamationCircleOutlined } from '@ant-design/icons';

import Alert from "antd/lib/alert";
import notification from "@/services/notification";
import {wrap as wrapDialog, DialogPropType} from "@/components/DialogWrapper";
import InputWithCopy from "@/components/InputWithCopy";
import HelpTrigger from "@/components/HelpTrigger";
import PlainButton from "@/components/PlainButton";

const API_SHARE_URL = "api/dashboards/{id}/share";
const API_EMAIL_URL = "api/dashboards/{id}/email";

class EmailDashboardDialog extends React.Component {
  static propTypes = {
    dashboard: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
    hasOnlySafeQueries: PropTypes.bool.isRequired,
    dialog: DialogPropType.isRequired,
  };

  formItemProps = {
    labelCol: {span: 8},
    wrapperCol: {span: 16},
    style: {marginBottom: 7},
  };

  constructor(props) {
    super(props);
    const {dashboard} = this.props;

    this.state = {
      group: [],
      saving: false,
      sending: false,
      emailList: localStorage['emailList'],
    };

    this.apiUrl = replace(API_EMAIL_URL, "{id}", dashboard.id);
    this.enabled = this.props.hasOnlySafeQueries || dashboard.publicAccessEnabled;
  }

  static get headerContent() {
    return (
      <React.Fragment>
        Share Dashboard
        <div className="modal-header-desc">
          Allow public access to this dashboard with a secret address. <HelpTrigger type="SHARE_DASHBOARD"/>
        </div>
      </React.Fragment>
    );
  }

  sendEmail = () => {
    const {dashboard} = this.props;
    this.setState({saving: true});

    axios
      .post(this.apiUrl,{emailList:this.state.emailList})
      .then(data => {
        console.log('sendEmail',data)
        dashboard.publicAccessEnabled = true;
        dashboard.public_url = data.public_url;
      })
      .catch(() => {
        notification.error("Failed to turn on sharing for this dashboard");
      })
      .finally(() => {
        this.setState({sending: false})
      });
  };


  onChange = checked => {
    if (checked) {
      this.enableAccess();
    } else {
      this.disableAccess();
    }
  };

  updateGroup=(index,key,value)=>{
    let group = [...this.state.group]
    let row = {...group[index]}
    row[key]=value
    group[index]=row
    this.setState({group})
  }

  delGroup=(index)=>{
    Modal.confirm({
      maskClosable:false,
    title: 'Confirm to delete group',
    icon: <ExclamationCircleOutlined />,
    content: 'Are your confirm to delete group :'+index,
    okText: 'ok',
      onOk:()=>{

    console.log('delete ',index)
    let group = [...this.state.group]
    group.splice(index,1)
    this.setState({group})
      },
    cancelText: 'cancel',
  });

  }

  addGroup=()=>{

    let group =[...this.state.group,{}]
    this.setState({group: group});
  }

  render() {
    const {dialog, dashboard} = this.props;
    const onFinish = (values) => {
      console.log('Success:', values);
      localStorage['emailList'] = values['emailList']

      this.setState({sending: true})
      this.sendEmail()
    };
    return (
      <Modal {...dialog.props} title={this.constructor.headerContent} footer={null}>
        <Form layout="horizontal"
              initialValues={{
                emailList: this.state.emailList,
              }}
              onFinish={onFinish}>
          {!this.props.hasOnlySafeQueries && (
            <Form.Item>
              <Alert
                message="For your security, sharing is currently not supported for dashboards containing queries with text parameters. Consider changing the text parameters in your query to a different type."
                type="error"
              />
            </Form.Item>
          )}

          <Form.Item name="emailList" label="Email list" {...this.formItemProps}>
            <Input.TextArea multiple={true} rows={4} cols={20}/>
          </Form.Item>

          <Form.Item   {...this.formItemProps} wrapperCol={{
            offset: 8,
            span: 16,
          }}>
            {this.state.group.map((row,index)=>{
              return (
                <table key={'group'+index}>
                  <tbody>
                  <tr>
                    <td>email list</td>
                    <td>
                      <Input.TextArea multiple={true}
                                      rows={4}
                                      cols={20}
                            value={row.email?row.email:''} onChange={(e)=>{
                      this.updateGroup(index,'email',e.target.value)
                    }}
                      />
                    </td>
                  </tr>
                  <tr>
                    <td>cronjob</td>
                    <td><Input value={row.cronjob?row.cronjob:''} onChange={(e)=>{
                      this.updateGroup(index,'cronjob',e.target.value)
                    }} /></td>
                  </tr>
                  <tr>
                    <td>params</td>
                    <td>

                    </td>
                  </tr>
                  <tr>
                    <td></td>
                    <td>
                      <Button htmlType="button" onClick={()=>this.delGroup(index)} >del</Button>
                    </td>
                  </tr>
                  </tbody>
                </table>
              )
            })}
              <Form.Item   {...this.formItemProps} wrapperCol={{
            offset: 8,
            span: 16,
          }}>
            <Button htmlType="button" onClick={this.addGroup} >add</Button>
          </Form.Item>
            <Button htmlType="submit" loading={this.state.sending}>Send Now</Button>
          </Form.Item>
        </Form>
      </Modal>
    );
  }
}

class EmailGroup{

}
export default wrapDialog(EmailDashboardDialog);
