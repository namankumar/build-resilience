import React from 'react';
import { View, Text, Button, Alert } from 'react-native';
import { recordWin } from '../api';

export default function WinScreen({ route, navigation }) {
  const { reflectionId, wins = [] } = route.params;

  async function complete(win) {
    try {
      await recordWin(reflectionId, win);
      navigation.navigate('Streak');
    } catch (err) {
      Alert.alert('Error', err.message);
    }
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>Choose a micro-win</Text>
      {wins.map((w) => (
        <Button key={w} title={w} onPress={() => complete(w)} />
      ))}
    </View>
  );
}
