// src/components/ResultList.js
import React from 'react';
import { List, ListItem, ListItemText, Typography, Divider } from '@mui/material';

const ResultList = ({ results }) => {
  if (!results || results.length === 0) {
    return <Typography sx={{ mt: 2 }}>没有查到相关记录</Typography>;
  }

  return (
    <List sx={{ mt: 2 }}>
      {results.map((item, index) => (
        <React.Fragment key={index}>
          <ListItem alignItems="flex-start">
            <ListItemText
              primary={`${item.company_name} - ${item.fund_name}`}
              secondary={
                <>
                  {item.fund_managers && item.fund_managers.length > 0 ? (
                    item.fund_managers.map((manager, idx) => (
                      <Typography key={idx} component="span" variant="body2" color="text.primary">
                        {manager.name} ({manager.phone}, {manager.email}) {manager.is_primary ? '【重点】' : ''}<br />
                      </Typography>
                    ))
                  ) : (
                    '无基金经理信息'
                  )}
                  剩余期限：{item.remaining_term} 年
                </>
              }
            />
          </ListItem>
          <Divider component="li" />
        </React.Fragment>
      ))}
    </List>
  );
};

export default ResultList;
