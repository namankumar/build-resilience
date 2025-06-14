import React, { useEffect, useState } from 'react';
import { View, Text, Button, ActivityIndicator, Alert } from 'react-native';
import { getStreak } from '../api';

export default function StreakScreen({ navigation }) {
  const [count, setCount] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStreak()
      .then((c) => {
        setCount(c);
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
      <Text>Your streak: {count}</Text>
      <Button title="See Wins" onPress={() => navigation.navigate('WinRack')} />
    </View>
  );
}
