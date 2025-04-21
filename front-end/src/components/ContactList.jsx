import React, { useState } from 'react';
import ContactModal from './ContactModal';
import './ContactList.css';

const ContactList = ({ contacts }) => {
  const [selectedContact, setSelectedContact] = useState(null);
  
  if (!contacts || contacts.length === 0) {
    return <div className="no-contacts">无联系人信息</div>;
  }
  
  const handleContactClick = (contact) => {
    setSelectedContact(contact);
  };
  
  const handleCloseModal = () => {
    setSelectedContact(null);
  };
  
  return (
    <div className="contact-list-container">
      <h5>所有联系人</h5>
      
      <div className="contact-list">
        {contacts.map((contact, idx) => (
          <div
            key={idx}
            className={`contact-card ${contact.is_leader ? 'leader-contact' : ''}`}
            onClick={() => handleContactClick(contact)}
          >
            <div className="contact-name">
              {contact.name}
              {contact.is_leader && <span className="leader-indicator">领导</span>}
            </div>
            <div className="contact-role">{contact.role}</div>
          </div>
        ))}
      </div>
      
      {selectedContact && (
        <ContactModal
          contact={selectedContact}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default ContactList; 