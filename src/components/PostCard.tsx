
interface PostCardProps {
  platform: string;
  content: string;
}

const PostCard = ({ platform, content }: PostCardProps) => {
  return (
    <div className="post-card">
      <strong>{platform}</strong>
      <p>{content}</p>
    </div>
  );
};

export default PostCard;
