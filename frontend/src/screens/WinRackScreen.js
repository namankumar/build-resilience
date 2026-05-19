import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, Alert } from 'react-native';
import { getWinrack } from '../api';

export default function WinRackScreen() {
  const [wins, setWins] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWinrack()
      .then((w) => {
        setWins(w);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        Alert.alert('Error', err.message);
      });
  }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>Your Wins:</Text>
      {wins.map((w) => (
        <Text key={w}>{w}</Text>
      ))}
    </View>
  );
}
