import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert } from 'react-native';
import { createReflection } from '../api';

export default function ReflectionInputScreen({ navigation }) {
  const [text, setText] = useState('');
  async function submit() {
    try {
      const reflection = await createReflection(text);
      navigation.navigate('Reframe', { reflectionId: reflection.id });
    } catch (err) {
      Alert.alert('Error', err.message);
    }
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>What's going on right now?</Text>
      <TextInput value={text} onChangeText={setText} style={{ borderWidth: 1, marginVertical: 12 }} />
      <Button title="Submit" onPress={submit} />
    </View>
  );
}
