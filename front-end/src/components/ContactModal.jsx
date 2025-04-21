import React from 'react';
import './ContactModal.css';

const ContactModal = ({ contact, onClose }) => {
  if (!contact) return null;

  return (
    <div className="contact-modal-overlay" onClick={onClose}>
      <div className="contact-modal-content" onClick={e => e.stopPropagation()}>
        <div className="contact-modal-header">
          <h3>
            {contact.name} 
            {contact.is_leader && <span className="leader-badge">领导</span>}
          </h3>
          <button className="contact-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="contact-modal-body">
          <div className="contact-detail-row">
            <label>角色:</label>
            <div>{contact.role || '-'}</div>
          </div>
          <div className="contact-detail-row">
            <label>工作电话:</label>
            <div>{contact.phone || '-'}</div>
          </div>
          <div className="contact-detail-row">
            <label>手机:</label>
            <div>{contact.mobile || '-'}</div>
          </div>
          <div className="contact-detail-row">
            <label>微信:</label>
            <div>{contact.wechat || '-'}</div>
          </div>
          <div className="contact-detail-row">
            <label>QQ:</label>
            <div>{contact.qq || '-'}</div>
          </div>
          <div className="contact-detail-row">
            <label>QT:</label>
            <div>{contact.qt || '-'}</div>
          </div>
          <div className="contact-detail-row">
            <label>电子邮件:</label>
            <div>{contact.email || '-'}</div>
          </div>
        </div>
        <div className="contact-modal-footer">
          <button className="contact-modal-button" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
};

export default ContactModal; 