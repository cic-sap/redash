import {replace} from "lodash";
import React from "react";
import {axios} from "@/services/axios";
import PropTypes from "prop-types";
import Switch from "antd/lib/switch";
import Modal from "antd/lib/modal";
import Form from "antd/lib/form";
import Input from "antd/lib/input";
import Button from "antd/lib/button";

import Alert from "antd/lib/alert";
import notification from "@/services/notification";
import {wrap as wrapDialog, DialogPropType} from "@/components/DialogWrapper";
import InputWithCopy from "@/components/InputWithCopy";
import HelpTrigger from "@/components/HelpTrigger";
import PlainButton from "@/components/PlainButton";

const API_SHARE_URL = "api/dashboards/{id}/share";

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
      saving: false,
      sending: false,
      emailList: '',
    };

    this.apiUrl = replace(API_SHARE_URL, "{id}", dashboard.id);
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

  enableAccess = () => {
    const {dashboard} = this.props;
    this.setState({saving: true});

    axios
      .post(this.apiUrl)
      .then(data => {
        dashboard.publicAccessEnabled = true;
        dashboard.public_url = data.public_url;
      })
      .catch(() => {
        notification.error("Failed to turn on sharing for this dashboard");
      })
      .finally(() => {
        this.setState({saving: false});
      });
  };

  disableAccess = () => {
    const {dashboard} = this.props;
    this.setState({saving: true});

    axios
      .delete(this.apiUrl)
      .then(() => {
        dashboard.publicAccessEnabled = false;
        delete dashboard.public_url;
      })
      .catch(() => {
        notification.error("Failed to turn off sharing for this dashboard");
      })
      .finally(() => {
        this.setState({saving: false});
      });
  };

  onChange = checked => {
    if (checked) {
      this.enableAccess();
    } else {
      this.disableAccess();
    }
  };

  render() {
    const {dialog, dashboard} = this.props;
    const onFinish = (values) => {
      console.log('Success:', values);
      this.setState({sending: true})
      setTimeout(() => {
        this.setState({sending: false})
      },2000)
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
            <Button htmlType="submit" loading={this.state.sending}>Send Now</Button>
          </Form.Item>
        </Form>
      </Modal>
    );
  }
}

export default wrapDialog(EmailDashboardDialog);
