from ..ressource_classes import EditorAdaptor, adaptionmethod, Resource


class mp3tagAdaptor(EditorAdaptor):
    
    @adaptionmethod
    def genre(self, backend_obj, value=None):
        return self.genre.target_with_args()
    
    
    
class mp3tagBase(Resource, mp3tagAdaptor.coupled_class()):
    allowed_file_extensions = [".mp3"]


mp3tagBase.set_prop("genre")