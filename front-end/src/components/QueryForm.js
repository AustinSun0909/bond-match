// src/components/BondQuery.js
import React, { useState } from 'react';
import { TextField, Button, Box, Typography, CircularProgress } from '@mui/material';
import axios from 'axios';

const BondQuery = () => {
  const [bondAbbr, setBondAbbr] = useState("");
  const [bondInfo, setBondInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleQuery = async () => {
    if (!bondAbbr) {
      setError("请输入债券简称");
      return;
    }
    setError("");
    setLoading(true);
    try {
      // 请求后端提供的Wind数据查询接口，例如：
      const response = await axios.get("http://127.0.0.1:8000/api/wind/bond/byabbr/", {
        params: { bond_abbr: bondAbbr }
      });
      setBondInfo(response.data);
    } catch (err) {
      console.error(err);
      setError("查询失败，请检查输入或稍后重试");
      setBondInfo(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5">债券信息查询</Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
        <TextField 
          label="债券简称" 
          variant="outlined" 
          value={bondAbbr} 
          onChange={(e) => setBondAbbr(e.target.value)} 
          sx={{ flexGrow: 1 }} 
        />
        <Button variant="contained" color="primary" sx={{ ml: 2 }} onClick={handleQuery} disabled={loading}>
          {loading ? <CircularProgress size={24} /> : "查询"}
        </Button>
      </Box>
      {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}
      {bondInfo && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body1">Wind代码: {bondInfo.wind_code}</Typography>
          <Typography variant="body1">发行主体: {bondInfo.issuer}</Typography>
          <Typography variant="body1">发行时间: {bondInfo.issuebegin}</Typography>
          <Typography variant="body1">发行期限: {bondInfo.term} 年</Typography>
        </Box>
      )}
    </Box>
  );
};

export default BondQuery;
