## 🧪 Development & Testing

### Google OAuth Authentication

The platform includes Google OAuth2 authentication for easy login.

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable **People API**  
3. Create OAuth 2.0 Credentials (Web application type)
4. Add redirect URI: `http://localhost:8000/accounts/google/login/callback/`
5. Copy **Client ID** and **Client Secret**
6. Set environment variables:
```bash
export GOOGLE_OAUTH_CLIENT_ID="your_client_id"
export GOOGLE_OAUTH_CLIENT_SECRET="your_client_secret"
```

See [GOOGLE_AUTH_SETUP.md](GOOGLE_AUTH_SETUP.md) for detailed instructions.

### Heart Sound Analysis Tool

The platform includes an advanced digital phonocardiography analysis tool for analyzing heart sounds:

**Features:**
- BPM detection (beats per minute) with species-aware algorithms
- S1/S2 classification (heart sound separation)
- HRV metrics (SDNN, RMSSD, pNN50)
- Adaptive peak detection for weak signals
- Noise filtering (20-150 Hz bandpass)

**Test Scripts:**

```bash
# Test with available WAV files
python test_cuore_tool.py

# Batch test all audio files
python test_all_audio_files.py

# Compare subject type effects
python test_final_subject_type.py
```

**Subject Type (Dog vs Human):**
- Dogs typically have higher heart rates (60-180 BPM)
- Humans typically have lower heart rates (50-100 BPM)
- Algorithm adapts threshold and S1/S2 pairing based on species

### Generating Realistic Test Data

The platform includes a management command to generate realistic dog profiles with historically accurate data:

```bash
# Generate 100 dogs with 30 days of health logs and medical history
python manage.py generate_real_dog_data --num-dogs 100 --days 30 --events 3
```

The generator creates:
- **Breed-appropriate profiles**: Realistic weights, dimensions, and activity levels
- **Historical health logs**: 30+ days of daily routine tracking (sleep, exercise, nutrition)
- **Medical event histories**: Correlated to breed predispositions and age
- **Diverse population**: Multiple breeds, ages (puppy to senior), and activity patterns

### Using Test Data

1. Login as `test_user_dog_data` (password: `test123456`)
2. Access any of the 103 dog profiles
3. Test AI diagnosis with different breeds and conditions
4. Run analytics on historical health patterns
5. Export veterinary dossiers for PDF/WhatsApp