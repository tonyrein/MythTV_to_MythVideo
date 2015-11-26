# from mythcontent.dto import TvRecording
import mythcontent.dto

class TvRecordingService:
    def list_recordings(self):
        return mythcontent.dto.list_recordings()
    
    def delete_recording(self, recording_to_delete):
        return recording_to_delete.erase()
