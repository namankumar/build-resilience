import React, { useEffect, useState } from 'react';
import { View, Text, Button, ActivityIndicator, Alert } from 'react-native';
import { getReframe } from '../api';

export default function ReframeScreen({ route, navigation }) {
  const { reflectionId } = route.params;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getReframe(reflectionId)
      .then((r) => {
        setData(r);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        Alert.alert('Error', err.message);
      });
  }, [reflectionId]);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>{data.text}</Text>
      {data.suggested_wins.map((w) => (
        <Text key={w}>{w}</Text>
      ))}
      <Button
        title="Take a small step"
        onPress={() => navigation.navigate('Win', { reflectionId, wins: data.suggested_wins })}
      />
    </View>
  );
}
