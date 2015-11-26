# from mythcontent.dto import TvRecording
import mythcontent.dto

class TvRecordingService:
    def list_recordings(self):
        return mythcontent.dto.list_recordings()
    
    def erase_recording(self, recording_to_erase):
        return recording_to_erase.erase()
